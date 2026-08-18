# Contracts

## Auralis Contract

Input:
- raw human intent

Output:
- structured interpretation
- refined prompt
- response capture

Rules:
- no silent transformations
- must preserve intent fidelity

---

## ChatGPT Bridge Contract

Must:
- send message reliably
- detect response completion
- return latest assistant message

Must NOT:
- duplicate messages
- lose session context