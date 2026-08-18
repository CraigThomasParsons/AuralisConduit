# OpenClaw Instructions

## Purpose
Use OpenClaw to automate browser interaction with ChatGPT.

---

## Tasks

### 1. Open ChatGPT
- Launch browser
- Navigate to chat.openai.com
- Ensure session is active

---

### 2. Inject Message
- Locate textarea
- Insert prompt
- Press Enter

---

### 3. Capture Response
- Wait for response completion
- Extract latest message

---

## Usage Pattern

OpenClaw should:
1. Receive prompt from Auralis
2. Execute browser actions
3. Return response text

---

## Notes

- Prefer stable selectors
- Avoid timing-only waits
- Use DOM observation if possible