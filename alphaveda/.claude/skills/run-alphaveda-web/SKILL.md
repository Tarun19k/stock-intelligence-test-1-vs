---
name: run-alphaveda-web
description: Launch and drive the AlphaVeda Next.js web app (alphaveda/web) — dev server or a live Vercel preview/production URL — with a headless-Chromium Playwright driver, screenshotting a fixed route list and reporting HTTP status + console errors per route. Use when asked to run, start, or screenshot AlphaVeda, or to confirm a change works in the real app.
---

# run-alphaveda-web

Drives `alphaveda/web` (Next.js) with `driver.mjs`, a one-shot Playwright script — not a REPL,
since this app doesn't need iterative interaction to prove it's running, just nav + screenshot +
console-error check per route. Re-run it whenever you need fresh screenshots.

## Dev server (local)

```bash
cd alphaveda/web
npm run dev &
timeout 30 bash -c 'until curl -sf http://localhost:3000 >/dev/null; do sleep 1; done'
```

Poll the port, don't `sleep N` — Turbopack's first compile can take several seconds.
`curl -sf` will itself report failure on a 500 (missing-env-var crash is expected without
`SUPABASE_SERVICE_KEY` set — see Known state below); if you need to confirm the server is
merely *listening* rather than *returning 200*, drop `-f` or check the driver's own status
output instead.

**Stop:** `lsof -ti:3000 -sTCP:LISTEN | xargs -r kill` before relaunching, or the next run hits
`EADDRINUSE` (`npm run dev &`'s `$!` is only the npm wrapper — it doesn't forward the kill to the
`next-server` child process it spawns).

## Drive

```bash
cd alphaveda/web
node ../.claude/skills/run-alphaveda-web/driver.mjs
```

Screenshots + `report.json` (per-route HTTP status + first 5 console errors) land in
`/tmp/shots` by default. Override with env vars:

| Var | Default | Use |
|---|---|---|
| `BASE_URL` | `http://localhost:3000` | Point at a live Vercel preview/production URL instead |
| `SHOT_DIR` | `/tmp/shots` | Where screenshots + `report.json` go |
| `ROUTES` | `/,/signals,/path,/instrument,/accuracy,/portfolio,/build-checklist` | Comma-separated route list |

## Known state (2026-08-17)

Without `SUPABASE_SERVICE_KEY` set in `alphaveda/web/.env.local`, every data-driven route
(`/`, `/signals`, `/path`, `/accuracy`, `/portfolio`, `/build-checklist`) 500s with a clean
Next.js error overlay pointing at `lib/supabase.ts:7` — expected, not a driver bug. `/instrument`
(no dynamic segment) correctly 404s and is the fastest way to confirm the app shell (nav,
branding, SEBI disclaimer footer) renders even when the DB-backed routes can't. Once the service
key is set, re-run the driver — all routes should report `status=200`.

## Gotchas

- **Module resolution: this driver lives outside `alphaveda/web/` on purpose** (see below), so
  a plain top-level `import '@playwright/test'` can't find it — Node's ESM resolver only walks
  up from the importing file's own path, and `alphaveda/web/node_modules` is a sibling, not an
  ancestor, of `alphaveda/.claude/skills/run-alphaveda-web/`. `driver.mjs` works around this with
  `createRequire(path.join(APP_DIR, 'package.json'))` — don't "simplify" this back to a plain
  `import`, it'll break the moment the driver isn't literally inside the app directory.
- **Browser binary version mismatch.** The installed `@playwright/test` version may expect a
  browser revision newer than what's pre-installed in this container
  (`/opt/pw-browsers/chromium-<rev>`). `driver.mjs` globs the actual installed revision and
  passes `executablePath` explicitly rather than trusting Playwright's own resolution — don't
  run `npx playwright install` to "fix" this (project convention: don't re-download browsers
  the container already has).
- **Outbound proxy for non-localhost URLs.** This container routes HTTPS through an agent proxy
  (`$HTTPS_PROXY`). `chromium.launch()` doesn't read that env var on its own — `driver.mjs`
  passes it explicitly via the `proxy` launch option, plus `--ignore-certificate-errors` (the
  proxy MITMs TLS with its own CA). Only kicks in for non-`localhost` `BASE_URL`.
- **Some external domains are egress-blocked outright**, even through the proxy (e.g.
  auto-generated `*.vercel.app` preview subdomains aren't on this environment's allow-list) —
  shows as `ERR_TUNNEL_CONNECTION_FAILED` with no fix available from inside the sandbox. When
  this happens, check deployment health via the Vercel MCP tools instead
  (`get_runtime_errors`, `get_deployment`) rather than a real screenshot.
- **Don't leave ad-hoc driver scripts loose in `alphaveda/web/`** — the repo's stop hook flags
  untracked files. Any throwaway variant of this driver belongs here, committed, not as a stray
  `.mjs` file at the app root.

## Troubleshooting

- **`EADDRINUSE` on relaunch:** previous `next dev` still holds port 3000 — see Stop above.
- **`browserType.launch: Executable doesn't exist`:** the globbed revision under
  `/opt/pw-browsers/` doesn't match what `@playwright/test` shipped — check
  `ls /opt/pw-browsers` and confirm `findChromiumBinary()` in `driver.mjs` still matches the
  directory naming convention there.
- **`net::ERR_TUNNEL_CONNECTION_FAILED` even on localhost:** the proxy launch option shouldn't
  fire for localhost — check `BASE_URL` isn't accidentally set to a non-local value.
