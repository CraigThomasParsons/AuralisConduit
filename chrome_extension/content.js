// content.js
// Auralis Chrome Extension - Content Script
// Injects prompts into ChatGPT and extracts responses via UI interaction.

console.log("%c AURALIS CONTENT SCRIPT LOADED ", "background: #222; color: #bada55; font-size: 20px");

window.auralisDebugLog = "";

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "EXECUTE_JOB") {
        executeAuralisJob(request.job).catch((error) => {
            reportJobFailure(request.job.id, error.message);
        });
    }
});

/**
 * Main execution flow for an Auralis job.
 * 
 * Orchestrates finding the input, sending the prompt,
 * waiting for the full response, and capturing the text.
 */
async function executeAuralisJob(job) {
    console.log("Auralis: Executing Job", job.id);
    document.body.style.border = "10px solid red"; // Processing visual indicator
    window.auralisDebugLog = "Started job. ";

    // Retrieve baseline message count to detect when a new response block is added.
    const initialMessageCount = countAssistantMessages();

    // Inject and send the prompt to ChatGPT.
    await injectAndSendPrompt(job.prompt);

    // Wait for the DOM to settle and generation to complete via MutationObserver.
    await waitForResponseCompletion(initialMessageCount);

    // Capture the final generated text using the UI copy button or fallback scraping.
    const responseText = await extractFinalAssistantResponse(initialMessageCount);

    // Signal completion back to the background script.
    document.body.style.border = "10px solid green"; // Success visual indicator
    chrome.runtime.sendMessage({
        type: "JOB_COMPLETE",
        data: {
            id: job.id,
            response: responseText,
            debug: window.auralisDebugLog
        }
    });
}

/**
 * Locates the ChatGPT prompt textarea dynamically.
 * 
 * Falls back through standard selectors to ensure resilience against minor DOM changes.
 */
function findPromptTextarea() {
    let area = document.getElementById("prompt-textarea");
    if (area) return area;

    area = document.querySelector('[data-testid="prompt-textarea"]');
    if (area) return area;

    area = document.querySelector('div.ProseMirror');
    if (area) return area;

    // Fallback: Use standard web accessibility tags
    area = document.querySelector('[role="textbox"]');
    if (area) return area;

    // Fallback: Just look for a literal textarea
    area = document.querySelector('textarea');
    if (area) return area;

    // Ultimate fallback for any major ChatGPT UI update
    const editables = document.querySelectorAll('div[contenteditable="true"]');
    if (editables.length > 0) {
        // The last content-editable is usually the main chat input
        return editables[editables.length - 1];
    }
    return null;
}

/**
 * Injects text into the prompt box and clicks send.
 */
async function injectAndSendPrompt(promptText) {
    let textarea = findPromptTextarea();

    // Poll for the textarea in case React is still rendering the page.
    if (!textarea) {
        window.auralisDebugLog += "Waiting for UI to render... ";
        for (let i = 0; i < 20; i++) {
            await sleep(500);
            textarea = findPromptTextarea();
            if (textarea) break;
        }
    }

    // Reject early to prevent orphaned operations if the UI is missing.
    if (!textarea) {
        throw new Error("Unable to locate ChatGPT prompt textarea.");
    }

    textarea.focus();

    // Handle both raw textarea and content-editable divs (ProseMirror).
    if (textarea.tagName === "TEXTAREA" || textarea.tagName === "INPUT") {
        textarea.value = promptText;
    } else {
        // Clear children and set innerText for contenteditable
        textarea.innerHTML = "";
        textarea.innerText = promptText;
    }

    // Trigger React state updates so the send button activates.
    textarea.dispatchEvent(new Event("input", { bubbles: true }));

    // Wait slightly for DOM to process the input event and render the send button.
    await sleep(500);

    const sendButton = document.querySelector('[data-testid="send-button"]');

    // Exit safely if the send button never appears.
    if (!sendButton) {
        throw new Error("Unable to locate ChatGPT send button.");
    }

    sendButton.click();
    window.auralisDebugLog += "Prompt sent. ";
}

/**
 * Reads the current number of assistant response blocks in the chat.
 */
function countAssistantMessages() {
    let assistantMsgs = document.querySelectorAll('.markdown');
    if (assistantMsgs.length === 0) {
        assistantMsgs = document.querySelectorAll("div[data-message-author-role='assistant']");
    }
    return assistantMsgs.length;
}

/**
 * Uses a highly efficient MutationObserver to monitor the page for DOM changes.
 * 
 * Instead of looking for fragile, constantly-changing ChatGPT-specific IDs (like 'stop-button'),
 * we simply monitor the entire DOM for character streaming. When the DOM receives streams
 * of new characters and then goes COMPLETELY quiet for 3 seconds, we know generation is complete.
 */
function waitForResponseCompletion(initialMessageCount) {
    return new Promise((resolve, reject) => {
        let lastMutationTime = Date.now();
        let hasStreamed = false;
        const MAX_TIMEOUT = 120000;

        const observer = new MutationObserver((mutations) => {
            for (let m of mutations) {
                // If text is being added or nodes are being added, it's streaming
                if (m.type === 'characterData' || (m.type === 'childList' && m.addedNodes.length > 0)) {
                    hasStreamed = true;
                    lastMutationTime = Date.now();
                }
            }
        });

        // Interval to check if mutations have settled for 3.5 seconds
        const settleInterval = setInterval(() => {
            const timeSinceLastMut = Date.now() - lastMutationTime;

            if (hasStreamed && timeSinceLastMut > 3500) {
                window.auralisDebugLog += "Generation finished (DOM settled). ";
                clearInterval(settleInterval);
                clearTimeout(timeoutId);
                observer.disconnect();
                resolve(true);
            }
        }, 1000);

        const timeoutId = setTimeout(() => {
            clearInterval(settleInterval);
            observer.disconnect();
            reject(new Error(`Timeout waiting for response completion after ${MAX_TIMEOUT}ms.`));
        }, MAX_TIMEOUT);

        observer.observe(document.body, { childList: true, subtree: true, characterData: true });
    });
}

/**
 * Finds the latest assistant response and extracts it safely.
 */
async function extractFinalAssistantResponse(initialMessageCount) {
    // Robustly find all markdown blocks on the page. ChatGPT wraps assistant text in .markdown
    let assistantMsgs = Array.from(document.querySelectorAll('.markdown'));

    // Fallback if .markdown is not used
    if (assistantMsgs.length === 0) {
        assistantMsgs = Array.from(document.querySelectorAll("div[data-message-author-role='assistant']"));
    }

    // Guard clause: ensure there is actually a new message to scrape.
    if (assistantMsgs.length <= initialMessageCount) {
        window.auralisDebugLog += "Error: No new messages found during extraction. ";
        throw new Error("No new response found to extract.");
    }

    // The most recent response block
    const latestMsgBlock = assistantMsgs[assistantMsgs.length - 1];
    // Target the most recent response block at the bottom of the chat.
    const newestMsg = assistantMsgs[assistantMsgs.length - 1];

    // Find the standard copy button inside this message block.
    let copyButton = newestMsg.querySelector('[data-testid="copy-turn-action-button"]');

    // If missing, climb up to the turn container and look again.
    if (!copyButton) {
        const turnContainer = newestMsg.closest('[data-testid^="conversation-turn"]');
        if (turnContainer) {
            copyButton = turnContainer.querySelector('[data-testid="copy-turn-action-button"]');
        }
    }

    if (copyButton) {
        copyButton.click();

        // Wait for the clipboard API to complete standard copy operation.
        await sleep(300);

        try {
            const clipboardText = await navigator.clipboard.readText();
            window.auralisDebugLog += `Copied via button (${clipboardText.length} chars). `;
            return clipboardText;
        } catch (error) {
            console.error("Auralis: Clipboard read failed:", error);
            window.auralisDebugLog += `Clipboard error: ${error.message}. `;
            // Do not throw; proceed to fallback extraction below.
        }
    } else {
        window.auralisDebugLog += "Copy button not found. ";
    }

    // Fallback: Manually scrape innerText from the markdown container if clipboard fails.
    return scrapeTextFromMessageBlock(newestMsg);
}

/**
 * Extracts inner text directly from the DOM as a last-resort fallback.
 */
function scrapeTextFromMessageBlock(messageElement) {
    const markdownContent = messageElement.querySelector('.markdown');
    const extractedText = markdownContent ? markdownContent.innerText : messageElement.innerText;

    window.auralisDebugLog += `DOM fallback extraction (${extractedText.length} chars). `;
    return extractedText;
}

/**
 * Dispatches an error payload back to the proxy/server.
 */
function reportJobFailure(jobId, errorMessage) {
    console.error("Auralis Job Error:", errorMessage);
    document.body.style.border = "10px solid orange"; // Error visual indicator

    // Dump the first 1000 chars of the page to help us debug what's actually rendering
    let pageContext = "(No body found)";
    try {
        if (document.body) {
            pageContext = document.body.innerText.substring(0, 1000).replace(/\n/g, '  ');
        }
    } catch (e) { }

    chrome.runtime.sendMessage({
        type: "JOB_FAIL",
        data: {
            id: jobId,
            error: `${errorMessage} | Page content seen: ${pageContext}`
        }
    });
}

/**
 * Syntactic sugar for setTimeout promises.
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
