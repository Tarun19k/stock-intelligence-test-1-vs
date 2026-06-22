# AlphaVeda Supabase — Credentials Inventory

## Project

| Field | Value |
|---|---|
| Name | alphaveda-prod |
| Reference ID | kowlkczswaglbmabygtl |
| Region | ap-south-1 (Mumbai / South Asia) |
| Org | Tarun19k's Org (`ferhzizogqwgdoxymgiy`) |
| Dashboard | https://supabase.com/dashboard/project/kowlkczswaglbmabygtl |
| Created | 2026-06-21 |
| Plan | Free tier |

## Where credentials live

| Credential | Location | Notes |
|---|---|---|
| SUPABASE_URL | `.env` (gitignored, workspace root) | `https://kowlkczswaglbmabygtl.supabase.co` |
| SUPABASE_ANON_KEY | `.env` (gitignored, workspace root) | Legacy JWT, prefix: `-neUU` |
| SUPABASE_SERVICE_KEY | `.env` (gitignored, workspace root) | Legacy JWT, prefix: `ChCZu` — ingest scripts only |
| SUPABASE_DB_PASSWORD | `.env` (gitignored, workspace root) | Direct Postgres connections only |
| GHA secrets (future) | GitHub repo → Settings → Secrets | Add before wiring ingest.yml cron |

## Key types

Supabase returns two key formats. AlphaVeda uses **legacy JWT** keys throughout:

| Type | Use |
|---|---|
| `SUPABASE_ANON_KEY` | Streamlit app reads (Row Level Security applies) |
| `SUPABASE_SERVICE_KEY` | Ingest scripts only — bypasses RLS; never in client code |

## Recovery

If `.env` is lost, re-fetch via:
```bash
SUPABASE_ACCESS_TOKEN=<personal-access-token> \
  curl https://api.supabase.com/v1/projects/kowlkczswaglbmabygtl/api-keys \
  -H "Authorization: Bearer <token>"
```
Personal access tokens: https://supabase.com/dashboard/account/tokens

## .env.example (safe to commit)

```
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_ANON_KEY=<anon-jwt>
SUPABASE_SERVICE_KEY=<service-jwt>
SUPABASE_DB_PASSWORD=<db-password>
ALPHAVEDA_COMMERCIAL=false
```
