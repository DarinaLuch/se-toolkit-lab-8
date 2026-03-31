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

<!-- Screenshot of a conversation with the agent in the Flutter web app -->

## Task 3A — Structured logging

**Happy-path log excerpt (request_started → request_completed, status 200):**

```
backend-1 | 2026-03-31 05:39:22,559 INFO [app.main] [trace_id=594a83120af4f4c7dbe29e4d0308e48c span_id=49f15afc5ac509e3 resource.service.name=Learning Management Service] - request_started
backend-1 | 2026-03-31 05:39:22,560 INFO [app.auth] [trace_id=594a83120af4f4c7dbe29e4d0308e48c span_id=49f15afc5ac509e3 resource.service.name=Learning Management Service] - auth_success
backend-1 | 2026-03-31 05:39:22,561 INFO [app.db.items] [trace_id=594a83120af4f4c7dbe29e4d0308e48c span_id=49f15afc5ac509e3 resource.service.name=Learning Management Service] - db_query
backend-1 | 2026-03-31 05:39:22,693 INFO [app.main] [trace_id=594a83120af4f4c7dbe29e4d0308e48c span_id=49f15afc5ac509e3 resource.service.name=Learning Management Service] - request_completed
```

**Error-path log excerpt (db_query ERROR after postgres stopped):**

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

