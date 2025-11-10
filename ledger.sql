-- Ledger schema (Postgres)
CREATE TABLE IF NOT EXISTS ctp_ledger (
  event_id UUID PRIMARY KEY,
  ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  actor TEXT NOT NULL,
  sub TEXT NOT NULL,
  jti TEXT NOT NULL,
  action TEXT NOT NULL CHECK (action IN ('access','revoke','renew','violation')),
  scopes TEXT[] NOT NULL,
  purpose TEXT NOT NULL,
  context_hash TEXT NOT NULL,
  policy_uri TEXT NOT NULL,
  decision TEXT NOT NULL CHECK (decision IN ('allow','deny')),
  hash_prev TEXT,
  hash_self TEXT
);

CREATE INDEX IF NOT EXISTS idx_ctp_ledger_jti ON ctp_ledger (jti);
CREATE INDEX IF NOT EXISTS idx_ctp_ledger_sub ON ctp_ledger (sub);
CREATE INDEX IF NOT EXISTS idx_ctp_ledger_ts ON ctp_ledger (ts);
