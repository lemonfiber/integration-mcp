# The HTTP mode's image: the server, its dependencies and Python, run as a user
# of its own.
#
# Everything is resolved on the build machine for the platform being built,
# from wheels alone, so both platforms build without an emulator and nothing is
# compiled. The final stage runs nothing: it copies. The state directory is made
# `0700` for the server's user, as the certificates contract requires, and is a
# volume, so a pinned certificate or a private root outlives the container.

# ghcr.io/astral-sh/uv:0.11.23
FROM --platform=$BUILDPLATFORM ghcr.io/astral-sh/uv@sha256:d0a0a753ab981624b49c97abc98821c1c09f4ca69d1ef5cee69c501be3d88479 AS uv

# python:3.14.6-slim-trixie
FROM --platform=$BUILDPLATFORM python@sha256:7bec7ddcddeff7975d6ba9b4be7dd6f6b2f55e7491539145e2978f7f97ce9144 AS build
ARG TARGETARCH
ARG VERSION=0.0.0
COPY --from=uv /uv /usr/local/bin/uv
WORKDIR /src
COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src ./src
RUN set -eu; \
    case "$TARGETARCH" in \
      amd64) platform=x86_64-manylinux_2_28 ;; \
      arm64) platform=aarch64-manylinux_2_28 ;; \
      *) echo "no image is built for $TARGETARCH" >&2; exit 1 ;; \
    esac; \
    uv version --frozen "$VERSION"; \
    uv export --frozen --no-dev --no-emit-project --output-file /tmp/requirements.txt; \
    uv pip install --no-build --require-hashes --python-version 3.14.6 --python-platform "$platform" \
      --target /app/site --requirement /tmp/requirements.txt; \
    uv build --wheel --out-dir /tmp/wheel; \
    for wheel in /tmp/wheel/*.whl; do \
      echo "lemonfiber-mcp @ file://$wheel --hash=sha256:$(sha256sum "$wheel" | cut -d ' ' -f 1)"; \
    done > /tmp/server.txt; \
    uv pip install --no-deps --no-build --require-hashes --python-version 3.14.6 --python-platform "$platform" \
      --target /app/site --requirement /tmp/server.txt; \
    mkdir -p /state

# python:3.14.6-slim-trixie
FROM python@sha256:7bec7ddcddeff7975d6ba9b4be7dd6f6b2f55e7491539145e2978f7f97ce9144
COPY --from=build /app/site /app/site
COPY --from=build --chown=65532:65532 --chmod=0700 /state /var/lib/lemonfiber-mcp
ENV PYTHONPATH=/app/site \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LEMONFIBER_LISTEN=0.0.0.0:8443 \
    LEMONFIBER_STATE=/var/lib/lemonfiber-mcp
USER 65532:65532
VOLUME ["/var/lib/lemonfiber-mcp"]
EXPOSE 8443
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD ["python", "-m", "lemonfiber_mcp", "health"]
ENTRYPOINT ["python", "-m", "lemonfiber_mcp"]
CMD ["http"]
