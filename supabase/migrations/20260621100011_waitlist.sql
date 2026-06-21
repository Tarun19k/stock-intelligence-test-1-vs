-- AlphaVeda Migration 0011: waitlist
-- Commercial intelligence: price_feedback and referred_by close Gap 10 (council condition C10).
-- converted_at set when waitlist user becomes a paying subscriber.

CREATE TABLE IF NOT EXISTS waitlist (
  id             SERIAL PRIMARY KEY,
  email          VARCHAR(200) NOT NULL UNIQUE,
  name           VARCHAR(200),
  signed_up_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  price_feedback VARCHAR(20) CHECK (
    price_feedback IN ('too_high','fair','too_low')
  ),
  referred_by    VARCHAR(200),          -- referral source
  converted_at   TIMESTAMPTZ            -- set when user becomes subscriber
);
