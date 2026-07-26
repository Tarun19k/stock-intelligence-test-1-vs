-- Migration 0018: add magnitude_hit and outcome columns to accuracy_outcomes
--
-- L1-D / RF-J (2026-07-26, 4-seat council: Lynch, Calibration Integrity,
-- UX/Accessibility, SEBI compliance/Varghese): the existing `hit` column is
-- DIRECTION-ONLY and stays that way (it already feeds downstream accuracy%/
-- streak calculations — redefining it would silently corrupt historical
-- interpretation). These two columns are additive:
--
-- magnitude_hit: TRUE if direction was correct AND the actual move reached
--                at least MAGNITUDE_TOLERANCE-adjusted magnitude/downside
--                target (see src/ingest/resolve_outcomes.py). DEFAULT FALSE
--                so existing unresolved rows don't imply a false magnitude
--                win.
-- outcome:       three-state 'WIN' | 'PARTIAL' | 'LOSS'. WIN = direction and
--                magnitude both hit; PARTIAL = direction hit, magnitude
--                missed; LOSS = direction missed. Nullable — not backfilled
--                for historical rows resolved before this migration; ingest.py
--                Step 6 populates it going forward for every new resolution.
--
-- Required by: ingest.py step 6 (batch upsert magnitude_hit + outcome)
--              resolve_outcomes.py (writes magnitude_hit boolean + outcome string)
--              web/app/accuracy/page.tsx (per-row Magnitude-Hit badge)
--
-- Apply: paste into Supabase Dashboard → SQL Editor, or `supabase db push`
--
-- PARITY-CHECK: column accuracy_outcomes.magnitude_hit
-- PARITY-CHECK: column accuracy_outcomes.outcome
--
-- This is the migration that caused the deploy-parity incident (2026-07-26): code
-- querying magnitude_hit/outcome was merged to main (auto-deploys to Vercel) before
-- this file was applied to production Supabase. /accuracy silently showed "0
-- Resolved" instead of 108 real rows — the Supabase query errored and a `?? []`
-- fallback swallowed it, with zero errors in Vercel logs. verify_deploy_parity.py
-- (CI, runs on every push to main) exists specifically to catch this class of gap
-- before it ships dark again.

ALTER TABLE accuracy_outcomes
    ADD COLUMN IF NOT EXISTS magnitude_hit BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS outcome VARCHAR(10);
