-- 20260727103949_accuracy_outcomes_add_magnitude.sql
-- This is the same real migration as alphaveda/supabase/migrations/0018_
-- accuracy_outcomes_add_magnitude.sql, copied under the CLI's actual
-- recorded version timestamp so the canonical (root) migration tree has a
-- matching file — the original 0018 file used a non-timestamp naming
-- convention the CLI doesn't recognize, which is why `supabase migration
-- list` showed this version as remote-only despite the file existing under
-- a different name in alphaveda/supabase/migrations/.
--
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

ALTER TABLE accuracy_outcomes
    ADD COLUMN IF NOT EXISTS magnitude_hit BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS outcome VARCHAR(10);
