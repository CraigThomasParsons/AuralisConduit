# Auralis Conduit

Auralis Conduit is a local-first bridge that turns ChatGPT into a **native layer of your development environment**. 

Rather than relying on the OpenAI API, Auralis uses a lightweight local Python server and a Chrome Extension to safely drive the ChatGPT web interface. Together, they allow your local scripts and systems to automatically send prompts, observe the response generation efficiently via DOM Observation (`MutationObserver`), and instantly capture the results back to your local file system.

Let’s build this cleanly, but keep it *hackable and fun*.

---

## 🏗️ Architecture: How It Works

The Auralis Conduit pipeline operates in a continuous true-automation loop completely hidden in the background tab:

1. **Inbox Polling**: The local backend (`auralis_server.py`) monitors an `inbox/` directory for new job folders containing markdown files (like `briefing.md`, `context.md`, `goals.md`).
2. **Browser Bridging**: The **Auralis Automation Client Chrome Extension** continuously polls the local server (`http://localhost:3000`) via a background worker.
3. **Prompt Injection**: When a job is detected, the extension's Content Script seamlessly injects the compiled prompt directly into the active ChatGPT web interface and clicks send.
4. **Resilient Observation**: The extension uses a highly-efficient `MutationObserver` to monitor the chat DOM. It intelligently waits for new message blocks to appear and the "Stop generating" indicator to vanish, ensuring the generation is 100% complete before taking action.
5. **Extraction**: The final response is cleanly captured (preferring ChatGPT's native clipboard copy mechanism, with a direct DOM scraping fallback if necessary).
6. **Handoff & Execution**: The markdown response is POSTed back to the local server, which archives the job into `archive/`, saves outputs to `runs/`, and extracts executable bash/python scripts into a safe `scratchpad/`.

---

## 📁 System Structure

```text
Auralis/
├── bin/          
│   ├── auralis_server.py   # The local HTTP server serving jobs & receiving completions
│   ├── auralis_proxy.py    # CLI tool to trigger individual jobs manually
│   └── lib/                # Shared file-system and parsing logic
├── chrome_extension/
│   ├── manifest.json       # Chrome Extension configuration
│   ├── background.js       # Background worker polling the server
│   └── content.js          # The DOM interaction and MutationObserver logic
├── inbox/                  # Drop job folders here to be picked up
├── outbox/                 # Handoff markers are stored here 
├── runs/                   # Captured responses and logs end up here
├── systemd/                # User Daemons for running the server headless
└── tools/
    └── restart_auralis.sh  # Script to easily restart the local python server
```

---

## 🚀 Installation Guide

Auralis operates securely without requiring API keys by driving the web interface you already have open. 

### 1. Install the Chrome Extension

1. Open Google Chrome and type `chrome://extensions/` in the address bar, then press **Enter**.
2. In the top right corner of the Extensions page, toggle on **Developer mode**.
3. A new menu bar will appear at the top left. Click the button that says **Load unpacked**.
4. A file browser window will open. Navigate to your cloned repository directory and select the `chrome_extension` folder.
5. The **Auralis Automation Client** will now appear in your active extensions. Keep a ChatGPT tab open in the background!

### 2. Run the Local Backend

Ensure you have Python 3 installed. You can run the server directly from the repository root:

```bash
python3 bin/auralis_server.py
```

*Alternatively, use the provided `systemd/` user services to run it constantly in the background.*

---

## 🎯 Usage Example

To trigger the automation, simply drop a folder containing a `briefing.md` file into the `inbox/` directory:

```bash
mkdir -p inbox/job_001
echo "Write a python script that prints Hello World" > inbox/job_001/briefing.md
```

If the server and extension are running, the background tab will instantly detect the job, execute the prompt in ChatGPT, wait for it to finish, and return the execution logs locally to `runs/job_001/`!
