# Sleep-Time Webhook Service - Deployment Guide

## Overview

This service enables **real-time sleep-time consolidation** for Scarlet when chatting via Letta ADE interface.

## Architecture

```
┌─────────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│  Letta ADE      │────▶│  Letta Server       │────▶│  Sleep-Webhook   │
│  (User Chat)    │     │  STEP_COMPLETE      │     │  (Port 8284)     │
└─────────────────┘     └─────────────────────┘     └────────┬─────────┘
                                                              │
                                                              ▼
                                                ┌──────────────────────────┐
                                                │  Sleep Agent             │
                                                │  (agent-bc713153-...)    │
                                                │  - Analyzes conversation │
                                                │  - Generates JSON        │
                                                │  - Stores to Qdrant      │
                                                └──────────────────────────┘
```

## Quick Start

### 1. Build and Start Services

```bash
cd scarlet

# Start all services
docker compose up -d

# Check logs
docker compose logs -f sleep-webhook
docker compose logs -f abiogenesis-letta
```

### 2. Verify Services

```bash
# Check webhook health
curl http://localhost:8284/health
# Expected: {"status":"healthy","counters":0}

# Check Letta
curl http://localhost:8283/v1/models
```

### 3. Test End-to-End

1. Open Letta ADE: http://localhost:8283
2. Start chat with Scarlet
3. Send 5 messages
4. Check webhook status:
   ```bash
   curl http://localhost:8284/status
   ```
5. Verify consolidation:
   - Check Qdrant for new memories
   - Check Letta logs for sleep agent activity

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LETTA_URL` | `http://localhost:8283` | Letta server URL |
| `SLEEP_THRESHOLD` | `5` | Messages before consolidation |
| `SLEEP_WEBHOOK_PORT` | `8284` | Webhook service port |
| `STEP_COMPLETE_KEY` | (empty) | Optional auth key |

### Docker Compose Configuration

```yaml
services:
  letta-server:
    environment:
      - LETTA_SLEEPTIME_ENABLED=false
      - STEP_COMPLETE_WEBHOOK=http://sleep-webhook:8284/webhooks/step-complete

  sleep-webhook:
    build: Dockerfile.webhook
    ports:
      - "8284:8284"
    environment:
      - LETTA_URL=http://letta-server:8283
      - SLEEP_THRESHOLD=5
```

## Troubleshooting

### Webhook Not Receiving Calls

1. Check Letta logs:
   ```bash
   docker compose logs abiogenesis-letta | grep -i webhook
   ```

2. Verify environment variable:
   ```bash
   docker exec abiogenesis-letta env | grep STEP_COMPLETE
   ```

3. Check network connectivity:
   ```bash
   docker exec abiogenesis-letta curl http://sleep-webhook:8284/health
   ```

### Consolidation Not Triggering

1. Check message counter:
   ```bash
   curl http://localhost:8284/status
   ```

2. Verify sleep agent exists:
   ```bash
   curl http://localhost:8283/v1/agents | jq '.[] | select(.name | contains("Sleep"))'
   ```

3. Check webhook logs:
   ```bash
   docker compose logs abiogenesis-sleep-webhook
   ```

## Manual Operations

### Reset Counter for Conversation

```bash
curl -X POST http://localhost:8284/reset/agent-0ef885f2-a9d9-4e9e-907a-7c6432004710
```

### View All Counters

```bash
curl http://localhost:8284/status
```

## Files

- `src/sleep_webhook.py` - Main service (FastAPI)
- `Dockerfile.webhook` - Docker image
- `tests/test_sleep_webhook.py` - Test suite
- `docker-compose.yml` - Service configuration
