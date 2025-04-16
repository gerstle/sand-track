FROM python:3.13-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-editable

ADD . /app

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv sync --frozen --no-editable

FROM python:3.13-slim

WORKDIR /app

RUN groupadd -g 1000 nonroot
RUN useradd -g 1000 -u 1000 nonroot

RUN mkdir /data
RUN mkdir /data/upload
RUN chown nonroot:nonroot /data
RUN chown nonroot:nonroot /data/upload


COPY --from=builder --chown=nonroot:nonroot /app/.venv /app/.venv
COPY --from=builder --chown=nonroot:nonroot /app/src /app/src
COPY --from=builder --chown=nonroot:nonroot /app/wsgi.py /app/
COPY --from=builder --chown=nonroot:nonroot /app/entrypoint.sh /app/

USER nonroot

CMD ["/app/entrypoint.sh"]