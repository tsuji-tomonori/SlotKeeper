FROM node:24.19.0-bookworm-slim AS node
FROM python:3.14-slim-bookworm AS runtime
COPY --from=ghcr.io/astral-sh/uv:0.12.19 /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
ENV PATH="/app/.venv/bin:$PATH" PYTHONPATH="/app/src:/app" PYTHONDONTWRITEBYTECODE=1
COPY src ./src
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--no-access-log"]
FROM runtime AS verify
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts && npx playwright install --with-deps chromium
RUN uv sync --frozen --no-install-project
COPY . .
RUN uv sync --frozen
RUN python tools/quintflow.py setup
ENV PATH="/app/.venv/bin:/app/node_modules/.bin:$PATH"
ENTRYPOINT ["python","-m","tools.project.verify"]
FROM node AS web
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts
COPY frontend ./frontend
RUN npm run build
CMD ["npm","exec","--","astro","preview","--root","frontend","--host","0.0.0.0","--port","4321"]
