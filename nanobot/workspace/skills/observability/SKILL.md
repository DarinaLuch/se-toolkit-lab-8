# Observability Skill

You have access to logs and traces from the LMS system.

## Available Tools

- **logs_search** — Search logs with LogsQL. Key queries:
  - Errors: `severity:ERROR`
  - DB errors: `event:db_query AND severity:ERROR`
  - By trace: `trace_id:"<id>"`
- **logs_error_count** — Count errors per service over a time window
- **traces_list** — List recent error trace IDs (sourced from logs)
- **traces_get** — Fetch all log entries for a trace_id to reconstruct what happened

## When user asks "What went wrong?" or "Check system health"

Execute these steps in order — do NOT stop early:

1. Call `logs_search` with query `severity:ERROR` and start `1h`
2. From the results, find the most recent entry where `trace_id` is non-empty
3. Call `traces_get` with that trace_id — this shows the full request timeline
4. Report ONE coherent summary:
   - How many errors and what kind (from step 1)
   - Which event failed and what the error message was
   - What the full request timeline looked like (from step 3)
   - Root cause in one plain sentence

**Always chain logs_search → traces_get. Never stop after just logs.**

## When user asks "Any errors in the last hour?"

1. Call `logs_error_count` for a quick summary
2. If errors > 0, call `logs_search` with `severity:ERROR` for details
3. Summarize concisely

## Formatting
- Error counts as numbers: "6 errors in the last hour"
- Trace IDs shortened to first 8 chars
- Never dump raw JSON — always summarize in prose
- Keep the full investigation under 10 lines
