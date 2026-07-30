-- 20260723104817_add_instruments_signal_gate_until.sql
-- RECONSTRUCTED 2026-07-30 from live schema introspection — no file existed
-- for this previously-applied version in either local migration tree.
--
-- This column is what gates TMCV (Tata Motors Commercial Vehicles, renamed
-- post-demerger 2025-10-29) from emitting any signal until 2027-01-01 —
-- confirmed live: TMCV is the only instrument currently gated
-- (signal_gate_until > now()). Consistent with G-CA's corporate-action-
-- adjustment concern already documented in GAP_REGISTER.md: TMCV's OHLCV
-- history only starts 2025-11-12, and the signal engine's return calc uses
-- the oldest row in its fetch window, so a short/discontinuous post-demerger
-- history would produce an unreliable signal if not gated.

ALTER TABLE instruments ADD COLUMN IF NOT EXISTS signal_gate_until DATE;
