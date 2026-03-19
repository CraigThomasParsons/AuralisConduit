// background.js
const SERVER_URL = "http://localhost:3000";
let processingJobId = null;

// Poll for jobs every 5 seconds using alarms (Manifest V3 compatible)
chrome.alarms.create("pollJob", { periodInMinutes: 0.1 }); // ~6 seconds

chrome.alarms.onAlarm.addListener(async (alarm) => {
    if (alarm.name === "pollJob") {
        // If we are already processing a job, do NOT fetch/start another.
        if (processingJobId) {
            return;
        }

        try {
            const res = await fetch(`${SERVER_URL}/job`);
            const job = await res.json();

            if (job && job.id) {
                console.log("Found job:", job);
                processingJobId = job.id; // LOCK
                processJob(job);
            }
        } catch (e) {
            // Server might be down, ignore
        }
    }
});

async function processJob(job) {
    // 1. Check if tab already exists for this URL
    // This prevents opening 100 tabs
    chrome.tabs.query({ url: job.url + "*" }, (tabs) => {
        if (tabs.length > 0) {
            // Tab exists, use it
            const tab = tabs[0];
            chrome.tabs.update(tab.id, { active: true });

            // Reload it? Or just inject? 
            // Reloading is safer to ensure clean state and content script re-run.
            chrome.tabs.reload(tab.id, {}, () => {
                // Wait for reload (content script will init)
                // Then we rely on message passing? 
                // Actually content script logic waits for 'EXECUTE_JOB' message.
                // So we must send it after reload complete.
                setTimeout(() => {
                    chrome.tabs.sendMessage(tab.id, {
                        type: "EXECUTE_JOB",
                        job: job
                    });
                }, 4000);
            });

        } else {
            // Create new tab
            chrome.tabs.create({ url: job.url }, (tab) => {
                setTimeout(() => {
                    chrome.tabs.sendMessage(tab.id, {
                        type: "EXECUTE_JOB",
                        job: job
                    });
                }, 5000);
            });
        }
    });
}

// Receive messages from content script (Job Done)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "JOB_COMPLETE") {
        console.log("Job Complete:", request.data.id);

        // Forward to server
        fetch(`${SERVER_URL}/job/complete`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(request.data)
        }).then(() => {
            // UNLOCK only after success
            processingJobId = null;
        });

        // Optional: Close tab?
        // chrome.tabs.remove(sender.tab.id);
    }
    else if (request.type === "JOB_FAIL") {
        console.log("Job Failed:", request.data.id);
        
        // Forward the failure safely to the backend server so the job is marked failed
        fetch(`${SERVER_URL}/job/fail`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(request.data)
        }).then(() => {
            processingJobId = null; // Release lock
        }).catch(() => {
            processingJobId = null; // Release lock even if server is unavailable
        });
    }
});
