const SERVER_URL = 'http://localhost:3000';
const MESSAGE_ATTEMPTS = 12;
const MESSAGE_RETRY_MS = 500;
let processingJobId = null;

chrome.alarms.create('pollJob', { periodInMinutes: 0.1 });
chrome.alarms.onAlarm.addListener(async (alarm) => {
    if (alarm.name !== 'pollJob' || processingJobId) return;
    try {
        const response = await fetch(`${SERVER_URL}/job`);
        if (!response.ok) throw new Error(`GET /job returned ${response.status}`);
        const job = await response.json();
        if (!job || !job.id) return;
        processingJobId = job.id;
        await processJob(job);
    } catch (error) {
        console.warn('Auralis polling/dispatch failed:', error);
        processingJobId = null;
    }
});

async function processJob(job) {
    const tab = await getOrCreateChatGptTab(job.url);
    await waitForTabComplete(tab.id, 20000);
    await sendMessageWithRetry(tab.id, { type: 'AURALIS_PING' }, (response) => response?.ready === true);
    await sendMessageWithRetry(tab.id, { type: 'EXECUTE_JOB', job }, (response) => response?.accepted === true);
}

async function getOrCreateChatGptTab(url) {
    const tabs = await chrome.tabs.query({ url: ['*://chatgpt.com/*', '*://*.chatgpt.com/*'] });
    if (tabs.length) return chrome.tabs.update(tabs[0].id, { active: true, url });
    return chrome.tabs.create({ active: true, url });
}

function waitForTabComplete(tabId, timeoutMs) {
    return new Promise((resolve, reject) => {
        let settled = false;
        const finish = (error) => {
            if (settled) return;
            settled = true;
            clearTimeout(timeout);
            chrome.tabs.onUpdated.removeListener(listener);
            error ? reject(error) : resolve();
        };
        const listener = (updatedId, changeInfo) => {
            if (updatedId === tabId && changeInfo.status === 'complete') finish();
        };
        const timeout = setTimeout(() => finish(new Error(`Tab ${tabId} did not finish loading.`)), timeoutMs);
        chrome.tabs.onUpdated.addListener(listener);
        chrome.tabs.get(tabId).then((tab) => { if (tab.status === 'complete') finish(); }).catch(finish);
    });
}

async function sendMessageWithRetry(tabId, message, acceptResponse) {
    let lastError;
    for (let attempt = 1; attempt <= MESSAGE_ATTEMPTS; attempt += 1) {
        try {
            const response = await chrome.tabs.sendMessage(tabId, message);
            if (acceptResponse(response)) return response;
            lastError = new Error(`Content script rejected ${message.type}.`);
        } catch (error) { lastError = error; }
        if (attempt < MESSAGE_ATTEMPTS) await sleep(MESSAGE_RETRY_MS);
    }
    throw lastError || new Error(`Unable to deliver ${message.type}.`);
}

chrome.runtime.onMessage.addListener((request) => {
    if (request.type === 'JOB_COMPLETE') acknowledgeResult('/job/complete', request.data, 'archived');
    else if (request.type === 'JOB_FAIL') acknowledgeResult('/job/fail', request.data, 'failed');
});

async function acknowledgeResult(path, data, expectedStatus) {
    try {
        if (!processingJobId || data.id !== processingJobId) throw new Error(`Ignoring result for non-active job ${data.id}.`);
        const response = await fetch(`${SERVER_URL}${path}`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok || payload.status !== expectedStatus) {
            throw new Error(`${path} acknowledgement failed (${response.status}): ${JSON.stringify(payload)}`);
        }
    } catch (error) {
        console.error('Auralis result acknowledgement failed:', error);
    } finally {
        processingJobId = null;
    }
}

function sleep(ms) { return new Promise((resolve) => setTimeout(resolve, ms)); }
