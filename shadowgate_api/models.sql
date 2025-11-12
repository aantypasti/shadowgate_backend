-- =========================
-- USERS
-- =========================
CREATE TABLE IF NOT EXISTS users (
  id               SERIAL PRIMARY KEY,
  username         TEXT UNIQUE NOT NULL,
  password_hash    TEXT NOT NULL,
  role             TEXT NOT NULL DEFAULT 'user',           -- 'user' | 'admin'
  ingame_username  TEXT,
  company_code     TEXT,
  fio_apikey       TEXT,
  bases            INTEGER NOT NULL DEFAULT 0,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================
-- LOAN ELIGIBILITY
-- =========================
-- Defines max amounts and interest per BASE COUNT and TYPE.
-- loan_type: 'std' (standard) | 'shp' (ship)
CREATE TABLE IF NOT EXISTS loan_eligibility (
  id         SERIAL PRIMARY KEY,
  bases      INTEGER NOT NULL,
  loan_type  TEXT    NOT NULL CHECK (loan_type IN ('std','shp')),
  max_amount BIGINT  NOT NULL,                -- whole currency units
  interest   NUMERIC(6,2) NOT NULL            -- % per week
);

-- Prevent duplicate rows for same bases/type/max
CREATE UNIQUE INDEX IF NOT EXISTS uq_eligibility_row
  ON loan_eligibility (bases, loan_type, max_amount);

-- =========================
-- LOANS
-- =========================
-- plan: 'stable' (repayment_rate determines duration) | 'interest-only'
-- status: 'active' | 'closed' | 'rejected'
CREATE TABLE IF NOT EXISTS loans (
  id                  SERIAL PRIMARY KEY,
  user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  loan_type           TEXT    NOT NULL CHECK (loan_type IN ('std','shp','refinance')),
  plan                TEXT    NOT NULL CHECK (plan IN ('stable','interest-only')),
  amount              BIGINT  NOT NULL CHECK (amount > 0),
  repayment_rate      NUMERIC(6,4) NOT NULL DEFAULT 0,     -- fraction of principal per week, 0..1
  interest_rate       NUMERIC(6,2) NOT NULL,               -- % per week
  total_interest_paid BIGINT  NOT NULL DEFAULT 0,
  duration_weeks      INTEGER,                              -- for 'interest-only'; NULL for 'stable'
  date_granted        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  end_date            TIMESTAMPTZ,                          -- optional; app may compute/fill
  status              TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','closed','rejected')),

  -- Plan-specific rules:
  -- stable:  repayment_rate > 0 AND duration_weeks IS NULL
  -- interest-only: repayment_rate = 0 AND duration_weeks > 0
  CONSTRAINT loans_plan_rules CHECK (
    (plan = 'stable' AND repayment_rate > 0 AND duration_weeks IS NULL)
    OR
    (plan = 'interest-only' AND repayment_rate = 0 AND duration_weeks IS NOT NULL AND duration_weeks > 0)
  )
);

-- One "active" loan per user.
-- NOTE: Do NOT use NOW() in index predicates (volatile). This stays time-agnostic;
-- app logic/view can handle "currently active by time" with end_date if needed.
CREATE UNIQUE INDEX IF NOT EXISTS uniq_active_loan_per_user
  ON loans (user_id)
  WHERE (status = 'active');

-- Helpful lookup indexes
CREATE INDEX IF NOT EXISTS idx_loans_user ON loans (user_id);
CREATE INDEX IF NOT EXISTS idx_loans_status ON loans (status);

-- =========================
-- (Optional) convenience view for time-aware active loans
-- =========================
-- Use this in queries when you want "active AND not past end_date".
-- This is SAFE here (views may use NOW()); just don't put NOW() into index predicates.
CREATE OR REPLACE VIEW active_loans_v AS
SELECT *
FROM loans
WHERE status = 'active'
  AND (end_date IS NULL OR end_date > NOW());
