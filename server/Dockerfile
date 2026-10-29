FROM node:22-bookworm-slim AS frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM node:22-bookworm-slim AS dealer-api
WORKDIR /database
COPY database/package*.json ./
RUN npm ci --omit=dev

FROM mongo:7.0
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" PYTHONUNBUFFERED=1 PORT=8000
COPY --from=dealer-api /usr/local/bin/node /usr/local/bin/node
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./
COPY --from=frontend /frontend/build ./frontend/build
COPY --from=dealer-api /database/node_modules ./database/node_modules
RUN mkdir -p /data/mongo && chown -R mongodb:mongodb /data /app
USER mongodb
EXPOSE 8000
ENTRYPOINT ["/opt/venv/bin/python", "start.py"]
