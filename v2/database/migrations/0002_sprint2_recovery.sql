BEGIN;

ALTER TABLE processing_job ADD COLUMN IF NOT EXISTS retry_count INTEGER NOT NULL DEFAULT 0;
ALTER TABLE processing_job ADD COLUMN IF NOT EXISTS recovery_status VARCHAR(32);
ALTER TABLE processing_job ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(255);
ALTER TABLE processing_job ADD COLUMN IF NOT EXISTS last_heartbeat_at TIMESTAMPTZ;

CREATE TABLE IF NOT EXISTS recovery_audit (
    id BIGSERIAL PRIMARY KEY,
    job_id VARCHAR(36) NOT NULL REFERENCES processing_job(id) ON DELETE CASCADE,
    decision VARCHAR(64) NOT NULL,
    reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_processing_job_last_heartbeat_at ON processing_job(last_heartbeat_at);
CREATE INDEX IF NOT EXISTS idx_processing_job_idempotency_key ON processing_job(idempotency_key);
CREATE INDEX IF NOT EXISTS idx_recovery_audit_job_id_created_at ON recovery_audit(job_id, created_at);

COMMIT;
