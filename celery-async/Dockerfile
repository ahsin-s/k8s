# syntax=docker/dockerfile:1.9

# ────────────────────────────────────────────────────────────────
# Builder stage: install dependencies with uv
# ────────────────────────────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Best practice: pin uv version for reproducibility
# You can update this digest periodically → docker build --pull ...
# ARG UV_VERSION=0.5.5   # or use :0.5-bookworm-slim tag
# but using python3.12-... variant is usually cleaner

WORKDIR /app

# Optimize uv & Python layers
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.12 \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy only the lockfile first → great cache hit when only code changes
COPY uv.lock pyproject.toml ./

# Install runtime dependencies only (no dev group)
# --no-dev is very important for production images
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Now copy the application code and install the project itself (editable=false)
COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ────────────────────────────────────────────────────────────────
# Final runtime stage – minimal image, no uv left behind
# ────────────────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy the virtualenv from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --from=builder /app /app

# Create non-root user (good security practice)
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app

USER appuser

# Activate venv in PATH
ENV PATH="/app/.venv/bin:$PATH"

# Default command — runs Celery worker
# Adjust queues, concurrency, loglevel, etc. via docker run / compose
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info", "--concurrency=1"]