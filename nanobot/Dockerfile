ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_NO_DEV=1 UV_PYTHON_DOWNLOADS=0

WORKDIR /app
COPY --from=workspace pyproject.toml uv.lock /app/
COPY pyproject.toml /app/nanobot/pyproject.toml
COPY --from=workspace mcp/ /app/mcp/
COPY --from=workspace nanobot-websocket-channel/nanobot-webchat/ /app/nanobot-websocket-channel/nanobot-webchat/
COPY --from=workspace nanobot-websocket-channel/nanobot-channel-protocol/ /app/nanobot-websocket-channel/nanobot-channel-protocol/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-workspace --package nanobot

COPY . /app/nanobot/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package nanobot

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 LANG=C.UTF-8
ENV PATH="/app/.venv/bin:$PATH"

RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

COPY --from=builder --chown=nonroot:nonroot /app /app

USER nonroot
WORKDIR /app

CMD ["python", "/app/nanobot/entrypoint.py"]
