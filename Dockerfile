# https://github.com/astral-sh/uv-docker-example/blob/main/multistage.Dockerfile

# An example using multi-stage image builds to create a final image without uv.

# First, build the application in the `/app` directory.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

ADD . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Install uwsgi in the virtualenv (requires build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential python3-dev \
    && uv pip install uwsgi==2.0.23 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Then, use a final image without uv
FROM python:3.12-slim-bookworm
# It is important to use the image that matches the builder, as the path to the
# Python executable must be the same, e.g., using `python:3.11-slim-bookworm`
# will fail.

# Install runtime dependencies for uwsgi
RUN apt-get update && apt-get install -y --no-install-recommends \
    libexpat1 \
    libxml2 \
    && rm -rf /var/lib/apt/lists/*

# Copy the application from the builder
COPY --from=builder --chown=app:app /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Run uwsgi.ini when the container launches
CMD ["bash", "-c", "flask translate compile && flask digest compile && PORT=\"${PORT:=5000}\" && uwsgi --ini uwsgi.ini --http :${PORT}"]
