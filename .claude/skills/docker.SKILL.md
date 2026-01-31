---
name: docker
description: Docker operations for ABIOGENESIS Scarlet environment
---

# Docker Operations Skill

## Quick Reference

| Action | Command |
|--------|---------|
| Start all | `cd scarlet && docker compose up -d` |
| Stop all | `cd scarlet && docker compose down` |
| Restart Letta | `docker compose restart abiogenesis-letta` |
| View logs | `docker compose logs -f abiogenesis-letta` |
| Check status | `docker ps \| grep abiogenesis` |

## Container Architecture

```
abiogenesis-letta     <- Main application (Letta framework)
├── Depends on: postgres (healthy), redis (healthy)
├── Ports: 8283
└── Volumes:
    - scarlet_postgres_data (via postgres)
    - scarlet_redis_data (via redis)
    - ./data:/app/data
    - ./prompts:/app/prompts
    - ./.env:/app/.env

abiogenesis-postgres  <- PostgreSQL database
└── Volume: scarlet_postgres_data

abiogenesis-redis     <- Redis cache
└── Volume: scarlet_redis_data
```

## Environment Variables Required

| Variable | Source | Purpose |
|----------|--------|---------|
| MINIMAX_API_KEY | `.env` | LLM provider |
| LETTA_PG_HOST | `docker-compose.yml` | Database connection |
| LETTA_REDIS_HOST | `docker-compose.yml` | Cache connection |
| POSTGRES_PASSWORD | `.env` | Database auth |

## Common Issues

### Letta not responding
```bash
# Check if running
docker ps | grep letta

# Check logs
docker logs abiogenesis-letta --tail 30

# Restart
docker compose restart abiogenesis-letta
```

### Database connection failed
```bash
# Verify postgres is healthy
docker ps | grep postgres

# Check postgres logs
docker logs abiogenesis-postgres

# Restart all services
docker compose down && docker compose up -d
```

### Volume issues
```bash
# List volumes
docker volume ls | grep scarlet

# Check volume usage
docker system df -v

# Remove orphaned volumes (CAREFUL - loses data)
docker volume prune -f
```

## Data Persistence

| Data Type | Location | Persists on restart? |
|-----------|----------|---------------------|
| PostgreSQL data | `scarlet_postgres_data` volume | YES |
| Redis data | `scarlet_redis_data` volume | YES |
| App data | `./data` bind mount | YES |
| Logs | Docker logs | NO |

## Adding New Services

When adding services to `docker-compose.yml`:

1. Add service under `services:`
2. Add volume under `volumes:` if named volume needed
3. Update network if needed (uses `abiogenesis-net`)
4. Add healthcheck for dependency services
5. Document in `docs/architecture/adr-*.md`
6. Update this skill if service-specific commands added

## Security Notes

- `.env` contains sensitive API keys - never commit to git
- `POSTGRES_PASSWORD` should be changed in production
- Consider `SECURE=true` for production deployments

## Verification Checklist

After any Docker change:
- [ ] All containers running: `docker ps | grep abiogenesis`
- [ ] Letta responding: `curl http://localhost:8283/v1/models`
- [ ] No errors in logs: `docker compose logs --tail 20`
- [ ] Data volumes exist: `docker volume ls | grep scarlet`
