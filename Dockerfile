FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend
RUN corepack enable && corepack prepare yarn@4.17.1 --activate
COPY frontend/package.json frontend/yarn.lock ./
RUN --mount=type=cache,target=/root/.yarn/berry/cache \
    YARN_CACHE_FOLDER=/root/.yarn/berry/cache \
    YARN_NODE_LINKER=node-modules \
    YARN_ENABLE_SCRIPTS=0 \
    yarn install --immutable
COPY frontend/ ./
ENV NITRO_PRESET=node-server
RUN yarn build

FROM node:22-alpine AS frontend
WORKDIR /app
COPY --from=frontend-builder /app/frontend/.output ./.output
USER node
EXPOSE 3000
ENV NITRO_HOST=0.0.0.0
ENV NITRO_PORT=3000
CMD ["node", ".output/server/index.mjs"]

FROM python:3.13-slim AS backend
WORKDIR /app
COPY api/ ./api/
RUN pip install --no-cache-dir \
    fastapi[standard] \
    piccolo[postgres] \
    pydantic-settings \
    emoji \
    uvicorn \
    starlette \
    fastapi-mail \
    scalar-fastapi \
    pycryptodome \
    pyjwt \
    pwdlib \
    python-multipart \
    minio \
    pillow \
    slowapi \
    "piccolo-api @ https://github.com/piccolo-orm/piccolo_api/archive/refs/tags/1.9.0.tar.gz"
WORKDIR /app/api
USER nobody
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
