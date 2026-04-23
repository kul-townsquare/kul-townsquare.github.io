# syntax=docker/dockerfile:1.6
# Blood on the Clocktower live session WebSocket backend.
#
# Base image pinned to digest for supply-chain auditability.
# To refresh:
#   docker pull node:22-alpine
#   docker image inspect node:22-alpine --format '{{index .RepoDigests 0}}'
# then update the FROM line and re-run `docker compose build`.
FROM node:22-alpine@sha256:8ea2348b068a9544dae7317b4f3aafcdc032df1647bb7d768a05a5cad1a7683f

WORKDIR /app

# Install production deps first for layer caching.
COPY package.json ./package.json
RUN npm install --omit=dev --omit=optional --no-audit --no-fund --loglevel=warn \
    && npm cache clean --force

# Copy the single server source file; no frontend, no devtools.
COPY index.js ./index.js

# Drop to non-root 'node' user (uid 1000) shipped with the upstream image.
USER node

EXPOSE 8081

# Keep NODE_ENV=development so index.js listens ws://0.0.0.0:8081 directly
# (via `new WebSocket.Server({ port: 8081 })`). Production mode requires
# cert.pem/key.pem and exposes a metrics endpoint on 8080 — both unwanted
# for this deployment. TLS termination happens at Cloudflare's edge in
# stage 3; the container is never reachable from host or LAN (enforced
# by compose port binding).
ENV NODE_ENV=development

CMD ["node", "index.js"]
