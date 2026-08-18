// Auralis Chrome Extension - ChatGPT content bridge.

const AURALIS = {
    composerSelectors: ['#prompt-textarea', '[data-testid="prompt-textarea"]', 'div.ProseMirror[contenteditable="true"]', 'form [role="textbox"][contenteditable="true"]', 'form textarea', 'div[contenteditable="true"]'],
    sendSelectors: ['[data-testid="send-button"]', 'button[aria-label="Send prompt"]', 'button[aria-label^="Send"]', 'form button[type="submit"]'],
    stopSelectors: ['[data-testid="stop-button"]', 'button[aria-label="Stop generating"]', 'button[aria-label^="Stop"]'],
    composerTimeoutMs: 15000, sendTimeoutMs: 10000, responseTimeoutMs: 120000, settleMs: 3500, pollMs: 250
};

let activeJobId = null;

if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.onMessage) {
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        if (request.type === 'AURALIS_PING') {
            sendResponse({ ready: true });
            return false;
        }
        if (request.type !== 'EXECUTE_JOB') return false;
        if (activeJobId) {
            sendResponse({ accepted: false, reason: `Already processing ${activeJobId}` });
            return false;
        }
        activeJobId = request.job.id;
        sendResponse({ accepted: true });
        executeAuralisJob(request.job)
            .catch((error) => reportJobFailure(request.job.id, error))
            .finally(() => { activeJobId = null; });
        return false;
    });
}

class AuralisStageError extends Error {
    constructor(stage, message, diagnostics = {}) {
        super(message);
        this.name = 'AuralisStageError';
        this.stage = stage;
        this.diagnostics = diagnostics;
    }
}

async function executeAuralisJob(job) {
    setBorder('red');
    const baselineTurns = getAssistantTurns();
    const composer = await waitForElement(AURALIS.composerSelectors, AURALIS.composerTimeoutMs, isUsableComposer);
    if (!composer) throw selectorError('composer', AURALIS.composerSelectors);
    await injectPrompt(composer, job.prompt);

    const sendButton = await waitForElement(AURALIS.sendSelectors, AURALIS.sendTimeoutMs, isClickable);
    if (!sendButton) throw selectorError('send', AURALIS.sendSelectors);
    sendButton.click();

    const responseTurn = await waitForResponseCompletion(baselineTurns);
    const responseText = await extractAssistantResponse(responseTurn);
    if (!responseText.trim()) throw new AuralisStageError('extract', 'The assistant response was empty.');

    setBorder('green');
    chrome.runtime.sendMessage({
        type: 'JOB_COMPLETE',
        data: { id: job.id, response: responseText, debug: 'composer:found; send:clicked; response:settled' }
    });
}

function setBorder(color) {
    if (document.body) document.body.style.border = `10px solid ${color}`;
}

function isVisible(element) {
    if (!element || !element.isConnected) return false;
    const style = typeof getComputedStyle === 'function' ? getComputedStyle(element) : null;
    if (style && (style.display === 'none' || style.visibility === 'hidden')) return false;
    const rect = typeof element.getBoundingClientRect === 'function' ? element.getBoundingClientRect() : { width: 1, height: 1 };
    return rect.width > 0 && rect.height > 0;
}

function isUsableComposer(element) {
    return isVisible(element) && !element.disabled && element.getAttribute('aria-disabled') !== 'true';
}

function isClickable(element) {
    return isUsableComposer(element);
}

function findFirst(selectors, predicate = () => true, root = document) {
    for (const selector of selectors) {
        for (const element of root.querySelectorAll(selector)) {
            if (predicate(element)) return { element, selector };
        }
    }
    return null;
}

async function waitForElement(selectors, timeoutMs, predicate) {
    const deadline = Date.now() + timeoutMs;
    while (Date.now() < deadline) {
        const match = findFirst(selectors, predicate);
        if (match) return match.element;
        await sleep(AURALIS.pollMs);
    }
    return null;
}

async function injectPrompt(composer, promptText) {
    composer.focus();
    if (composer instanceof HTMLTextAreaElement || composer instanceof HTMLInputElement) {
        const prototype = composer instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
        Object.getOwnPropertyDescriptor(prototype, 'value').set.call(composer, promptText);
    } else {
        composer.replaceChildren();
        composer.textContent = promptText;
    }
    const InputEventType = typeof InputEvent === 'function' ? InputEvent : Event;
    composer.dispatchEvent(new InputEventType('input', { bubbles: true, inputType: 'insertText', data: promptText }));
    composer.dispatchEvent(new Event('change', { bubbles: true }));
}

function getAssistantTurns() {
    const explicit = Array.from(document.querySelectorAll('[data-message-author-role="assistant"]'));
    if (explicit.length) return explicit;
    return Array.from(document.querySelectorAll('[data-testid^="conversation-turn-"]')).filter((turn) => Boolean(turn.querySelector('.markdown, [data-message-author-role="assistant"]')));
}

function isGenerating() {
    return Boolean(findFirst(AURALIS.stopSelectors, isVisible));
}

async function waitForResponseCompletion(baselineTurns) {
    const baselineCount = baselineTurns.length;
    const deadline = Date.now() + AURALIS.responseTimeoutMs;
    let responseTurn = null;
    let lastText = '';
    let lastChangeAt = Date.now();
    let observer = null;
    try {
        while (Date.now() < deadline) {
            if (!responseTurn || !responseTurn.isConnected) {
                const currentTurns = getAssistantTurns();
                responseTurn = currentTurns.length > baselineCount ? currentTurns[currentTurns.length - 1] : null;
                if (responseTurn) {
                    lastText = responseTurn.innerText || responseTurn.textContent || '';
                    lastChangeAt = Date.now();
                    observer = new MutationObserver(() => {
                        const text = responseTurn.innerText || responseTurn.textContent || '';
                        if (text !== lastText) { lastText = text; lastChangeAt = Date.now(); }
                    });
                    observer.observe(responseTurn, { childList: true, subtree: true, characterData: true });
                }
            }
            if (responseTurn) {
                const text = responseTurn.innerText || responseTurn.textContent || '';
                if (text !== lastText) { lastText = text; lastChangeAt = Date.now(); }
                if (text.trim() && !isGenerating() && Date.now() - lastChangeAt >= AURALIS.settleMs) return responseTurn;
            }
            await sleep(AURALIS.pollMs);
        }
    } finally {
        if (observer) observer.disconnect();
    }
    throw new AuralisStageError('response', `Timed out after ${AURALIS.responseTimeoutMs}ms waiting for a new assistant turn.`, {
        baselineCount, currentCount: getAssistantTurns().length, generating: isGenerating()
    });
}

async function extractAssistantResponse(turn) {
    const copyButton = turn.querySelector('[data-testid="copy-turn-action-button"]') || turn.closest('[data-testid^="conversation-turn-"]')?.querySelector('[data-testid="copy-turn-action-button"]');
    if (copyButton && isClickable(copyButton)) {
        copyButton.click();
        await sleep(300);
        try {
            const copied = await navigator.clipboard.readText();
            if (copied.trim()) return copied;
        } catch (_) { /* DOM fallback below. */ }
    }
    const content = turn.matches('.markdown') ? turn : turn.querySelector('.markdown') || turn;
    return content.innerText || content.textContent || '';
}

function selectorError(stage, selectors) {
    return new AuralisStageError(stage, `Unable to locate a usable ${stage} control.`, { selectors, url: location.href });
}

function reportJobFailure(jobId, error) {
    setBorder('orange');
    chrome.runtime.sendMessage({
        type: 'JOB_FAIL',
        data: { id: jobId, error: error.message || String(error), stage: error.stage || 'unknown', diagnostics: error.diagnostics || {} }
    });
}

function sleep(ms) { return new Promise((resolve) => setTimeout(resolve, ms)); }

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AURALIS, findFirst, isVisible, isClickable, isUsableComposer };
}
