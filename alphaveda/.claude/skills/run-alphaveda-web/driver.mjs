#!/usr/bin/env node
// driver.mjs — one-shot Playwright driver for alphaveda/web.
// Navs a fixed route list, screenshots each, captures console errors + HTTP status.
// Run from alphaveda/web/ (needs its node_modules for @playwright/test resolution).
//
// Usage:
//   node ../.claude/skills/run-alphaveda-web/driver.mjs               # localhost:3000
//   BASE_URL=https://<preview>.vercel.app node ../.claude/skills/run-alphaveda-web/driver.mjs
//   SHOT_DIR=/tmp/shots ROUTES=/,/signals node ../.claude/skills/run-alphaveda-web/driver.mjs
//
// Why this exists (gotchas hit building it, 2026-08-17):
// - The installed @playwright/test version expects a browser revision newer than what's
//   pre-installed in this container (/opt/pw-browsers/chromium-1194) — chromium.launch()'s
//   default download-managed binary 404s. Fix: pass executablePath explicitly at the revision
//   that's actually on disk (glob it — don't hardcode the revision number, it will drift).
// - This container's outbound HTTPS goes through an agent proxy (env HTTPS_PROXY /
//   https_proxy). chromium.launch() does NOT read that env var automatically — pass
//   `proxy: { server: process.env.HTTPS_PROXY }` explicitly for any non-localhost BASE_URL,
//   plus `--ignore-certificate-errors` (the proxy MITMs TLS with its own CA). localhost
//   traffic doesn't go through the proxy and needs neither.
// - Even with the proxy configured, this environment's egress policy may block specific
//   external domains outright (e.g. one-off *.vercel.app preview subdomains aren't
//   allow-listed) — that shows as ERR_TUNNEL_CONNECTION_FAILED with no fix on this side.
//   If that happens, fall back to checking deployment health via the Vercel MCP tools
//   (get_runtime_errors, get_deployment) instead of a real screenshot.

import * as fs from 'node:fs';
import * as path from 'node:path';
import { createRequire } from 'node:module';

// This driver lives at alphaveda/.claude/skills/run-alphaveda-web/, not inside
// alphaveda/web/ itself (kept out of the app dir on purpose — see SKILL.md's
// "Don't leave ad-hoc driver scripts loose in alphaveda/web/" gotcha). Node's ESM
// resolver only walks up from the importing file's own path, so a plain top-level
// `import '@playwright/test'` can't find alphaveda/web/node_modules from here.
// createRequire() pointed at the app's package.json resolves it correctly instead.
const APP_DIR = path.resolve(import.meta.dirname, '../../../web');
const require = createRequire(path.join(APP_DIR, 'package.json'));
const { chromium } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';
const SHOT_DIR = process.env.SHOT_DIR || '/tmp/shots';
const ROUTES = (process.env.ROUTES || '/,/signals,/path,/instrument,/accuracy,/portfolio,/build-checklist').split(',');

fs.mkdirSync(SHOT_DIR, { recursive: true });

function findChromiumBinary() {
  const root = '/opt/pw-browsers';
  if (!fs.existsSync(root)) return undefined;
  const rev = fs.readdirSync(root).find((d) => /^chromium-\d+$/.test(d));
  if (!rev) return undefined;
  const bin = path.join(root, rev, 'chrome-linux', 'chrome');
  return fs.existsSync(bin) ? bin : undefined;
}

const launchOpts = { args: ['--no-sandbox'] };
const bin = findChromiumBinary();
if (bin) launchOpts.executablePath = bin;

const isLocal = /^https?:\/\/(localhost|127\.0\.0\.1)/.test(BASE_URL);
if (!isLocal && (process.env.HTTPS_PROXY || process.env.https_proxy)) {
  launchOpts.proxy = { server: process.env.HTTPS_PROXY || process.env.https_proxy };
  launchOpts.args.push('--ignore-certificate-errors');
}

const browser = await chromium.launch(launchOpts);
const page = await browser.newPage();

const report = {};
for (const route of ROUTES) {
  const errs = [];
  const onConsole = (msg) => { if (msg.type() === 'error') errs.push(msg.text()); };
  page.on('console', onConsole);
  let status = null;
  try {
    const resp = await page.goto(`${BASE_URL}${route}`, { waitUntil: 'networkidle', timeout: 20000 });
    status = resp ? resp.status() : null;
  } catch (e) {
    status = `NAV_ERROR: ${e.message.split('\n')[0]}`;
  }
  const name = route === '/' ? 'home' : route.replace(/\//g, '');
  await page.screenshot({ path: path.join(SHOT_DIR, `${name}.png`), fullPage: true }).catch(() => {});
  page.off('console', onConsole);
  report[route] = { status, errors: errs.slice(0, 5) };
  console.log(`--- ${route} --- status=${status}`);
  if (errs.length) console.log('  console errors:', errs.slice(0, 3));
}

await browser.close();
fs.writeFileSync(path.join(SHOT_DIR, 'report.json'), JSON.stringify(report, null, 2));
console.log('\nDONE. Screenshots + report.json in', SHOT_DIR);
