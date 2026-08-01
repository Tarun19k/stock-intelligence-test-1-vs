// Single source of truth for the cold-start observation threshold.
// Was previously duplicated as two different magic numbers (OBSERVATION_THRESHOLD=30
// on signals/page.tsx, INSTRUMENT_OBSERVATION_THRESHOLD=20 on instrument/[ticker]/page.tsx)
// -- same underlying concept (has this instrument earned a calibrated confidence read),
// two different unexplained values that could silently drift apart. Consolidated
// 2026-08-01 (calibration-integrity finding) to the value that actually matches the
// live backend calibration formula in engine.py -- 30 is real-backed, 20 had no
// documented justification.
export const OBSERVATION_THRESHOLD = 30
