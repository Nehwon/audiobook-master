BEGIN;

CREATE TABLE IF NOT EXISTS processing_job (
    id VARCHAR(36) PRIMARY KEY,
    folder_id VARCHAR(255) NOT NULL,
    status VARCHAR(32) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS processing_step (
    id BIGSERIAL PRIMARY KEY,
    job_id VARCHAR(36) NOT NULL REFERENCES processing_job(id) ON DELETE CASCADE,
    name VARCHAR(120) NOT NULL,
    status VARCHAR(32) NOT NULL,
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    details JSONB
);

CREATE TABLE IF NOT EXISTS folder_state (
    folder_id VARCHAR(255) PRIMARY KEY,
    status VARCHAR(32) NOT NULL,
    last_job_id VARCHAR(36) REFERENCES processing_job(id) ON DELETE SET NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS validation_result (
    id BIGSERIAL PRIMARY KEY,
    folder_id VARCHAR(255) NOT NULL,
    validation_key VARCHAR(120) NOT NULL,
    status VARCHAR(32) NOT NULL,
    payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS processing_error (
    id BIGSERIAL PRIMARY KEY,
    job_id VARCHAR(36) REFERENCES processing_job(id) ON DELETE SET NULL,
    folder_id VARCHAR(255),
    error_code VARCHAR(80) NOT NULL,
    user_message TEXT NOT NULL,
    technical_message TEXT,
    stacktrace TEXT,
    retryable VARCHAR(8) NOT NULL DEFAULT 'false',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS outbox_event (
    id BIGSERIAL PRIMARY KEY,
    aggregate_type VARCHAR(64) NOT NULL,
    aggregate_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_processing_job_status_updated_at ON processing_job(status, updated_at);
CREATE INDEX IF NOT EXISTS idx_processing_job_folder_id ON processing_job(folder_id);
CREATE INDEX IF NOT EXISTS idx_processing_step_job_id_status ON processing_step(job_id, status);
CREATE INDEX IF NOT EXISTS idx_folder_state_status_updated_at ON folder_state(status, updated_at);
CREATE INDEX IF NOT EXISTS idx_validation_result_folder_id ON validation_result(folder_id);
CREATE INDEX IF NOT EXISTS idx_processing_error_job_id ON processing_error(job_id);
CREATE INDEX IF NOT EXISTS idx_processing_error_folder_id ON processing_error(folder_id);
CREATE INDEX IF NOT EXISTS idx_outbox_event_created_at ON outbox_event(created_at);

COMMIT;
