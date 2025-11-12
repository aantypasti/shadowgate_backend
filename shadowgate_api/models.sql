-- Users table for Shadowgate
CREATE TABLE IF NOT EXISTS users (
  id            SERIAL PRIMARY KEY,
  username      TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role          TEXT DEFAULT 'user',
  ingame_username TEXT,
  company_code  TEXT,
  fio_apikey    TEXT,
  bases         INTEGER DEFAULT 0,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);
-- ===== LOAN ELIGIBILITY (if not already created) =====
CREATE TABLE IF NOT EXISTS loan_eligibility (
  id           SERIAL PRIMARY KEY,
  bases        INTEGER NOT NULL,
  loan_type    TEXT    NOT NULL CHECK (loan_type IN ('std','shp')),
  max_amount   BIGINT  NOT NULL,                 -- whole currency units
  interest     NUMERIC(6,2) NOT NULL             -- % per week
);

-- Prevent accidental duplicates for a given bases/type/max
CREATE UNIQUE INDEX IF NOT EXISTS uq_eligibility_row
  ON loan_eligibility (bases, loan_type, max_amount);

-- ===== LOANS =====
CREATE TABLE IF NOT EXISTS loans (
  id                   SERIAL PRIMARY KEY,
  user_id              INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  loan_type            TEXT    NOT NULL CHECK (loan_type IN ('std','shp','refinance')),
  plan                 TEXT    NOT NULL CHECK (plan IN ('stable','interest-only')),
  amount               BIGINT  NOT NULL CHECK (amount > 0),
  repayment_rate       NUMERIC(6,4) NOT NULL DEFAULT 0 CHECK (repayment_rate >= 0 AND repayment_rate <= 1),
  interest_rate        NUMERIC(6,2) NOT NULL,          -- % per week
  total_interest_paid  BIGINT  NOT NULL,               -- whole currency units
  duration_weeks       INTEGER NOT NULL CHECK (duration_weeks > 0),
  date_granted         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  end_date             TIMESTAMPTZ NOT NULL,
  status               TEXT    NOT NULL DEFAULT 'active' CHECK (status IN ('active','closed','rejected'))
);

-- One active loan per user (active AND not past end_date)
CREATE UNIQUE INDEX IF NOT EXISTS uniq_active_loan_per_user
ON loans (user_id)
WHERE (status = 'active' AND end_date > NOW());
