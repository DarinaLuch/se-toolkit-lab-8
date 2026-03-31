"""MCP tools for querying VictoriaLogs and VictoriaTraces."""
from __future__ import annotations
import os
import httpx
from pydantic import BaseModel, Field
from mcp.types import TextContent
import json

def _logs_url() -> str:
    return os.environ.get("NANOBOT_VICTORIALOGS_URL", "http://localhost:42010")

def _traces_url() -> str:
    return os.environ.get("NANOBOT_VICTORIATRACES_URL", "http://localhost:42011")

# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------
class _LogsSearchArgs(BaseModel):
    query: str = Field(description="LogsQL query, e.g. 'event:db_query AND severity:ERROR'")
    limit: int = Field(default=20, ge=1, le=200)
    start: str = Field(default="1h", description="Time range, e.g. '1h', '30m', '24h'")

class _LogsErrorCountArgs(BaseModel):
    start: str = Field(default="1h", description="Time range, e.g. '1h', '30m', '24h'")

class _TracesListArgs(BaseModel):
    service: str = Field(default="backend", description="Service name")
    limit: int = Field(default=10, ge=1, le=50)

class _TracesGetArgs(BaseModel):
    trace_id: str = Field(description="Trace ID to fetch — looks up all log entries sharing this trace_id")

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------
async def logs_search(args: _LogsSearchArgs) -> list[TextContent]:
    url = f"{_logs_url()}/select/logsql/query"
    params = {"query": args.query, "limit": args.limit, "start": args.start}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
    lines = [l for l in resp.text.strip().split("\n") if l]
    records = []
    for line in lines:
        try:
            records.append(json.loads(line))
        except Exception:
            pass
    summary = []
    for r in records:
        summary.append({
            "time": r.get("_time", ""),
            "event": r.get("event", r.get("_msg", "")),
            "severity": r.get("severity", ""),
            "path": r.get("path", ""),
            "status": r.get("status", ""),
            "error": r.get("error", ""),
            "trace_id": r.get("trace_id", ""),
        })
    return [TextContent(type="text", text=json.dumps(summary, ensure_ascii=False))]

async def logs_error_count(args: _LogsErrorCountArgs) -> list[TextContent]:
    url = f"{_logs_url()}/select/logsql/query"
    params = {"query": "severity:ERROR", "limit": 200, "start": args.start}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
    lines = [l for l in resp.text.strip().split("\n") if l]
    counts: dict[str, int] = {}
    for line in lines:
        try:
            r = json.loads(line)
            svc = r.get("service.name", "unknown")
            counts[svc] = counts.get(svc, 0) + 1
        except Exception:
            pass
    result = {"total_errors": sum(counts.values()), "by_service": counts, "window": args.start}
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

async def traces_list(args: _TracesListArgs) -> list[TextContent]:
    """List recent traces by finding unique trace_ids in recent error logs."""
    url = f"{_logs_url()}/select/logsql/query"
    params = {"query": "severity:ERROR", "limit": args.limit * 3, "start": "1h"}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
    lines = [l for l in resp.text.strip().split("\n") if l]
    seen: dict[str, dict] = {}
    for line in lines:
        try:
            r = json.loads(line)
            tid = r.get("trace_id", "")
            if tid and tid not in seen:
                seen[tid] = {
                    "traceID": tid,
                    "time": r.get("_time", ""),
                    "event": r.get("event", ""),
                    "error": r.get("error", ""),
                }
                if len(seen) >= args.limit:
                    break
        except Exception:
            pass
    return [TextContent(type="text", text=json.dumps(list(seen.values()), ensure_ascii=False))]

async def traces_get(args: _TracesGetArgs) -> list[TextContent]:
    """Fetch all log entries for a trace_id to reconstruct the request timeline."""
    url = f"{_logs_url()}/select/logsql/query"
    # Query all log entries that share this trace_id
    query = f'trace_id:"{args.trace_id}"'
    params = {"query": query, "limit": 50, "start": "24h"}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
    lines = [l for l in resp.text.strip().split("\n") if l]
    spans = []
    for line in lines:
        try:
            r = json.loads(line)
            spans.append({
                "time": r.get("_time", ""),
                "event": r.get("event", r.get("_msg", "")),
                "severity": r.get("severity", ""),
                "error": r.get("error", ""),
                "status": r.get("status", ""),
                "path": r.get("path", ""),
                "duration_ms": r.get("duration_ms", ""),
            })
        except Exception:
            pass
    if not spans:
        return [TextContent(type="text", text=f"No log entries found for trace_id {args.trace_id}")]
    return [TextContent(type="text", text=json.dumps(spans, ensure_ascii=False))]
