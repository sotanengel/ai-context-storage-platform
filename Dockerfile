# syntax=docker/dockerfile:1

FROM python:3.11-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:0.11.2 /uv /uvx /bin/

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libmagic1 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock README.md LICENSE ./

RUN --mount=type=secret,id=takumi_guard_token,required=false \
    if [ -f /run/secrets/takumi_guard_token ]; then \
        export UV_INDEX_FLATT_TECH_PASSWORD="$(cat /run/secrets/takumi_guard_token)"; \
    else \
        export UV_INDEX_URL="https://pypi.org/simple/"; \
    fi \
    && uv sync --frozen --no-dev --all-extras --no-install-project

COPY src ./src

RUN --mount=type=secret,id=takumi_guard_token,required=false \
    if [ -f /run/secrets/takumi_guard_token ]; then \
        export UV_INDEX_FLATT_TECH_PASSWORD="$(cat /run/secrets/takumi_guard_token)"; \
    else \
        export UV_INDEX_URL="https://pypi.org/simple/"; \
    fi \
    && uv sync --frozen --no-dev --all-extras \
    && uv run python -m spacy download en_core_web_sm

FROM python:3.11-slim-bookworm AS runtime

RUN apt-get update \
    && apt-get install -y --no-install-recommends libmagic1 curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system formaforge \
    && useradd --system --gid formaforge --create-home --home-dir /home/formaforge formaforge \
    && mkdir -p /data/bronze \
    && chown -R formaforge:formaforge /data /home/formaforge

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/pyproject.toml /app/pyproject.toml
COPY --from=builder /app/README.md /app/README.md
COPY --from=builder /app/LICENSE /app/LICENSE
COPY scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod +x /usr/local/bin/docker-entrypoint.sh \
    && chown -R formaforge:formaforge /app /home/formaforge

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    FORMAFORGE_TRANSPORT=streamable-http \
    FORMAFORGE_HOST=0.0.0.0 \
    FORMAFORGE_PORT=8000 \
    FORMAFORGE_STORAGE_DIR=/data/bronze

USER formaforge

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -s -o /dev/null "http://127.0.0.1:${FORMAFORGE_PORT}/" || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["formaforge", "serve"]
