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

<img width="1916" height="1073" alt="3 1 2" src="https://github.com/user-attachments/assets/1d6c541a-5e7b-46d4-9350-3c27a222df3c" />
<img width="1912" height="985" alt="3 1 1" src="https://github.com/user-attachments/assets/bba95376-9604-4ecd-b3d9-881f6f6ed775" />


## Task 3B — Traces

<img width="1037" height="362" alt="3 2" src="https://github.com/user-attachments/assets/f78e0655-5b08-45b7-985b-16a5ad20402f" />


## Task 3C — Observability MCP tools

<!-- Paste agent responses to "any errors in the last hour?" under normal and failure conditions -->

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->

## Task 3C — Observability MCP tools

**Normal conditions — "Any errors in the last hour?"**

> I'll check for errors in the last hour using the logging system.
> Good news! There were **0 errors** in the last hour across all services. The system is running smoothly. 🎉

**Failure conditions (postgres stopped, 3 failed requests) — "Any errors in the last hour?"**

> I'll check for errors in the last hour using the logging system.
> Yes, there are **3 errors** in the last hour, all from the **Learning Management Service**. Let me get more details about these errors:
>
> **Yes, there are 3 errors in the last hour.**
>
> All errors are from the **Learning Management Service** and appear to be related to database connectivity issues:
>
> | Time | Event | Error |
> |------|-------|-------|
> | 05:39:22 | db_query | `[Errno -2] Name or service not known` |
> | 05:39:21 | db_query | `[Errno -2] Name or service not known` |
> | 05:39:20 | db_query | `[Errno -2] Name or service not known` |
>
> The error `Name or service not known` indicates a **DNS resolution failure** — the service could not reach the database host.
