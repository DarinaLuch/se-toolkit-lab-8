"""Runtime entrypoint: injects env vars into config.json then launches nanobot gateway."""
import json
import os
import tempfile

def main() -> None:
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    workspace = os.path.join(os.path.dirname(__file__), "workspace")

    with open(config_path) as f:
        cfg = json.load(f)

    # LLM provider
    cfg["providers"]["custom"]["apiKey"] = os.environ["LLM_API_KEY"]
    cfg["providers"]["custom"]["apiBase"] = os.environ["LLM_API_BASE_URL"]
    cfg["agents"]["defaults"]["model"] = os.environ.get("LLM_API_MODEL", "coder-model")

    # Gateway host/port
    cfg["gateway"]["host"] = os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS", "0.0.0.0")
    cfg["gateway"]["port"] = int(os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT", "18790"))

    # Webchat channel
    cfg["channels"]["webchat"] = {
        "enabled": True,
        "host": os.environ.get("NANOBOT_WEBCHAT_CONTAINER_ADDRESS", "0.0.0.0"),
        "port": int(os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT", "8765")),
        "accessKey": os.environ.get("NANOBOT_ACCESS_KEY", ""),
        "allowFrom": ["*"],
    }

    # MCP server env vars
    cfg["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_BACKEND_URL"] = os.environ["NANOBOT_LMS_BACKEND_URL"]
    cfg["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_API_KEY"] = os.environ["NANOBOT_LMS_API_KEY"]

    # Write resolved config to a temp file
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(cfg, tmp, indent=2)
    tmp.close()

    os.execvp("nanobot", ["nanobot", "gateway", "--config", tmp.name, "--workspace", workspace])

if __name__ == "__main__":
    main()
