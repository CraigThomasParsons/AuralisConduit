# Sprint0 Goal: Contracts and Scope Lock

## Purpose

Define the three canonical contracts and the shared filesystem layout before any code changes. Everything downstream depends on this being frozen first.

## Target Outcomes

- Auralis → Krax job contract is JSON-schema complete and reviewed
- Krax → Vera output contract is JSON-schema complete and reviewed
- Vera → Auralis verdict contract is JSON-schema complete and reviewed
- Shared filesystem layout is documented and agreed
- Gap register lists what each agent is missing relative to contracts
- Reuse mapping exists showing how TYS contracts and runtime rules fold back into ArcaneArcadeMachineFactory
- No code written yet — contracts first

## Acceptance Criteria

- All three contracts are complete JSON schemas with required/optional fields, types, and example values
- Filesystem layout is one canonical diagram — no ambiguity
- Gap register names the missing piece per agent with the owning sprint
- Each contract includes Arcane compatibility notes for correlation, attempt, status, and artifact path semantics
- An implementer could read this sprint's output and know exactly what to build in Sprint1+
