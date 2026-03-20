# Task 3: Real Vera — Vision LLM Evaluator

## Goals

- Send screenshot + acceptance criteria to a Vision LLM
- Parse the LLM response into a structured PASS/FAIL verdict with observations
- This is the "reality check" that prevents hallucination loops

## Requirements

- evaluator sends: screenshot (base64), acceptance criteria text, expected_behavior from krax_output.json
- evaluator receives: structured assessment from Vision LLM
- response is parsed into: `status` (pass/fail/partial), `confidence` (0.0–1.0), `observations` (list)
- evaluator is configurable: model selection in `Vera/config.yaml`
- evaluator timeout: 60 seconds; on timeout → status: error

## Acceptance Criteria

- given a screenshot and `expected_behavior: "Button is red and has rounded corners"`:
  - evaluator returns a verdict dict with status, confidence, and observations
  - observations include at least one entry per acceptance criterion
- if Vision LLM API is unreachable: status = error, clear error message in observations

## Implementation Steps

1. Update `Vera/bin/ai_evaluator.py`:
   - load screenshot from `evidence/<job_id>/screenshot.png`
   - build prompt: "Here is a screenshot. The expected behavior is: <expected_behavior>. Evaluate and return: {status, confidence, observations: [{check, result, detail}]}"
   - call Vision LLM API (default: OpenAI gpt-4o with vision)
   - parse JSON from response (or extract it from markdown block)
   - return structured verdict dict
2. Add to `Vera/config.yaml`: `evaluator: {provider: openai, model: gpt-4o, timeout: 60}`
3. Handle API errors: catch exceptions, return `{status: error, confidence: 0.0, observations: [{check: "api_call", result: "fail", detail: "<error>"}]}`

## Handoff Artifacts

- `Vera/bin/ai_evaluator.py` updated
- sample verdict from a real evaluation appended to this file under Completion Notes
