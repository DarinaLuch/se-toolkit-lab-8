# Lab 8 — Report

## Task 1A — Bare agent

**Q: What is the agentic loop?**

The agentic loop is the core reasoning-and-action cycle that enables AI agents to work autonomously toward goals. The basic cycle: Observe → Think → Act → Repeat. In nanobot, the loop is built-in — it receives input, sends context to the LLM with available tools, parses tool calls, executes them, feeds results back, and repeats until done.

**Q: What labs are available in our LMS?**

The agent read from local workspace files and described the lab tasks (Set Up the Agent, Deploy the Agent, etc.) — it did NOT call the real LMS backend. This is expected behavior without MCP tools.

## Task 1B — Agent with LMS tools

**Q: What labs are available?**

lab-01, lab-02, lab-03, lab-04, lab-05, lab-06, lab-07, lab-08 — real data from the LMS backend via MCP tools.

**Q: Describe the architecture of the LMS system**

The agent described: LMS Backend (FastAPI), PostgreSQL, React Dashboard, Caddy reverse proxy, Nanobot Agent, Qwen Code API, Flutter Web UI, MCP Servers, OpenTelemetry Collector, VictoriaLogs, VictoriaTraces. All services communicate over the lms-network Docker network.

## Task 1C — Skill prompt

**Q: Show me the scores** (without specifying a lab)

The agent called lms_labs first, listed all 8 labs, then asked: "Which lab would you like to see scores for?" — correct behavior per the skill prompt.

## Task 2A — Deployed agent

<!-- Paste a short nanobot startup log excerpt showing the gateway started inside Docker -->

## Task 2B — Web client

<img width="951" height="992" alt="task2" src="https://github.com/user-attachments/assets/69beadca-5229-47c9-9bf8-30940aa42216" />

## Task 3A — Structured logging


**Happy-path log excerpt (request_started → request_completed, status 200):**

<img width="1916" height="1073" alt="3 1 2" src="https://github.com/user-attachments/assets/1d6c541a-5e7b-46d4-9350-3c27a222df3c" />
<img width="1912" height="985" alt="3 1 1" src="https://github.com/user-attachments/assets/bba95376-9604-4ecd-b3d9-881f6f6ed775" />


```
backend-1 | 2026-03-31 05:39:22,559 INFO [app.main] [trace_id=594a83120af4f4c7dbe29e4d0308e48c span_id=49f15afc5ac509e3 resource.service.name=Learning Management Service] - request_started
backend-1 | 2026-03-31 05:39:22,560 INFO [app.auth] [trace_id=594a83120af4f4c7dbe29e4d0308e48c span_id=49f15afc5ac509e3 resource.service.name=Learning Management Service] - auth_success
backend-1 | 2026-03-31 05:39:22,561 INFO [app.db.items] [trace_id=594a83120af4f4c7dbe29e4d0308e48c span_id=49f15afc5ac509e3 resource.service.name=Learning Management Service] - db_query
backend-1 | 2026-03-31 05:39:22,693 INFO [app.main] [trace_id=594a83120af4f4c7dbe29e4d0308e48c span_id=49f15afc5ac509e3 resource.service.name=Learning Management Service] - request_completed
```


**Error-path log excerpt (db_query ERROR after postgres stopped):**

<img width="1037" height="362" alt="3 2" src="https://github.com/user-attachments/assets/f78e0655-5b08-45b7-985b-16a5ad20402f" />

```
backend-1 | 2026-03-31 05:56:51,570 INFO [app.db.items] [trace_id=75a04e25c0afe46e278bae3e8170e9d4 span_id=35652be9a2dd3c11 resource.service.name=Learning Management Service] - db_query
backend-1 | 2026-03-31 05:56:51,658 ERROR [app.db.items] [trace_id=75a04e25c0afe46e278bae3e8170e9d4 span_id=35652be9a2dd3c11 resource.service.name=Learning Management Service] - db_query
```

VictoriaLogs query used: `_stream:{service="backend"} AND level:error`

## Task 3B — Traces

**Healthy trace** — `GET /items/` with postgres running:
- `Learning Management Service` root span — HTTP request, ~134ms, status OK
- `auth` child span — Bearer token validation, ~1ms, status OK
- `db_query` child span — PostgreSQL SELECT, ~130ms, status OK

**Error trace** — `GET /items/` with postgres stopped:
- `Learning Management Service` root span — status ERROR, ~88ms
- `db_query` child span — status ERROR, error: `[Errno -2] Name or service not known`

trace_id=75a04e25c0afe46e278bae3e8170e9d4 from the error log matched the trace in VictoriaTraces UI, confirming log-to-trace correlation.

## Task 3C — Observability MCP tools

**Normal conditions — "Any errors in the last hour?"**

> I'll check for errors in the last hour using the logging system.
> Good news! There were **0 errors** in the last hour across all services. The system is running smoothly.

**Failure conditions (postgres stopped, 3 failed requests) — "Any errors in the last hour?"**

> Yes, there are **3 errors** in the last hour, all from the **Learning Management Service**.
>
> | Time | Event | Error |
> |------|-------|-------|
> | 05:39:22 | db_query | `[Errno -2] Name or service not known` |
> | 05:39:21 | db_query | `[Errno -2] Name or service not known` |
> | 05:39:20 | db_query | `[Errno -2] Name or service not known` |
>
> The error indicates a DNS resolution failure — the service could not reach the database host.

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->


## Task 4A — Multi-step investigation

**Question asked:** "What went wrong?"

**Agent response:**

I found 4 errors in the last hour from the Learning Management Service. Let me investigate what those errors are:

Found the issue! There are **4 database connection errors** in the last hour. All errors show:
**Error:** `[Errno -2] Name or service not known`

This is a **DNS resolution failure** - the system is trying to connect to a database service but cannot resolve the hostname. Let me get more details from one of the traces:

## What Went Wrong: Database Connection Failure
**Root Cause:** DNS resolution failure for the database service
**Details:**
- **4 errors** in the last hour (starting around 05:56 UTC)
- **Error message:** `[Errno -2] Name or service not known`
- **Affected service:** Learning Management Service (LMS)
- **Impact:** Database queries are failing, causing requests to return 404 errors

The agent used both log evidence (db_query errors with severity:ERROR) and trace evidence (traces_get to reconstruct the request timeline).

## Task 4B — Proactive health check

The agent created a cron job (ID: `1c3663ab`) running every 2 minutes.

**Proactive failure report posted automatically at 06:56 UTC:**

Health Check Report (2026-03-31 06:56 UTC)
⚠️ Errors detected!
- Error count (last 2 min): 1 error
- Service affected: Learning Management Service
- Error type: unhandled_exception
- Endpoint: /learners/
- Trace ID: c09f03df83885b9bf349309d858c9189

Timeline:
1. 06:54:22.874 — Request started on /learners/
2. 06:54:22.876 — Auth succeeded
3. 06:54:22.937 — Unhandled exception occurred

The agent posted this report proactively without being asked, while the failure was still present.

## Task 4C — Bug fix and recovery

### Root cause
The planted bug was in `backend/app/db/learners.py`. The `read_learners` and `create_learner` functions had no `try/except` block, so when PostgreSQL was down, the raw database exception propagated directly to FastAPI's `unhandled_exception_handler` in `main.py`. This logged `unhandled_exception` instead of `db_query`, hiding the real error from the observability tools.

By contrast, `backend/app/db/items.py` already had the correct pattern: a `try/except` that logs `db_query` with the error field before re-raising.

### Fix
Added `try/except` logging to both `read_learners` and `create_learner` in `backend/app/db/learners.py`, matching the pattern in `items.py`:
```python
try:
    logger.info("db_query", extra={"event": "db_query", "table": "learner", "operation": "select"})
    # ... db operation ...
except Exception as exc:
    logger.error(
        "db_query",
        extra={"event": "db_query", "table": "learner", "operation": "select", "error": str(exc)},
    )
    raise
```

### Post-fix failure check
After rebuilding and stopping PostgreSQL, the agent's "What went wrong?" response showed the real underlying failure:

- Error type: db_query (not unhandled_exception)
- Error message: [Errno -2] Name or service not known (DNS resolution failure for database)
- Additional: connection is closed (existing connections dropped)
- Endpoints affected: /items/ → 404, /learners/ → 500

### Healthy follow-up
After restarting PostgreSQL, the proactive health check reported:

Health Check Report — System looks healthy! ✅
- Time window: Last 2 minutes
- Total errors: 0
- Services with errors: None
- No issues detected.
