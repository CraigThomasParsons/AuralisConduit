# Sprint5 Goal: Hardening, Retry, and Observability

## Purpose

Make the loop production-reliable. Contract validation enforced at every boundary. Retry logic for transient failures (server down, Grok timeout). Audit trail that gives a clear picture of every job's journey. Dashboard or summary script for status at a glance.

## Target Outcomes

- Contract violations rejected at every entry point with logged errors
- Transient failures are retried automatically (Grok timeout, Vera API error)
- Every job has a complete human-readable audit trail from Auralis→Krax→Vera
- A summary script shows current loop status across all in-flight and recent jobs
- System can run unattended overnight without getting stuck

## Acceptance Criteria

- inject a job with a missing required field → it is rejected at the entry point with a clear log, not silently corrupted
- kill Krax server mid-job → Krax recovers on restart and retries the job
- kill Vera daemon mid-job → Vera recovers on restart and retries
- run `python3 tools/loop_status.py` → human-readable summary of all active and recent jobs
