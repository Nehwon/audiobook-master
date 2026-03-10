BEGIN;

-- Types métier pour l'inventaire scanné depuis le dossier input
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'library_item_type') THEN
        CREATE TYPE library_item_type AS ENUM ('FILE', 'FOLDER', 'ARCHIVE');
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'library_item_status') THEN
        CREATE TYPE library_item_status AS ENUM (
            'NEW',
            'VALID',
            'DECOMPRESSED',
            'RENAMED',
            'PROCESSING_PENDING',
            'PROCESSING',
            'PROCESSED',
            'DELETED',
            'ERROR'
        );
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'plugin_install_status') THEN
        CREATE TYPE plugin_install_status AS ENUM (
            'INSTALLED',
            'DISABLED',
            'UNINSTALLED',
            'ERROR'
        );
    END IF;
END
$$;

-- Inventaire canonique des entrées découvertes dans le dossier input.
CREATE TABLE IF NOT EXISTS library_item (
    id BIGSERIAL PRIMARY KEY,
    parent_id BIGINT REFERENCES library_item(id) ON DELETE SET NULL,
    root_scan_path TEXT NOT NULL,
    absolute_path TEXT NOT NULL,
    relative_path TEXT NOT NULL,
    item_type library_item_type NOT NULL,
    status library_item_status NOT NULL DEFAULT 'NEW',

    -- Champs demandés pour le suivi métier
    initial_size_bytes BIGINT,
    final_size_bytes BIGINT,
    files_to_process_count INTEGER NOT NULL DEFAULT 0,
    source_name TEXT NOT NULL,
    renamed_name TEXT,
    error_text TEXT,

    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_library_item_absolute_path UNIQUE (absolute_path),
    CONSTRAINT ck_library_item_processed_is_file
        CHECK (status <> 'PROCESSED' OR item_type = 'FILE')
);

CREATE INDEX IF NOT EXISTS idx_library_item_parent_id ON library_item(parent_id);
CREATE INDEX IF NOT EXISTS idx_library_item_type_status ON library_item(item_type, status);
CREATE INDEX IF NOT EXISTS idx_library_item_status_updated_at ON library_item(status, updated_at);
CREATE INDEX IF NOT EXISTS idx_library_item_last_seen_at ON library_item(last_seen_at);

-- Historique des transitions d'état pour audit et debugging.
CREATE TABLE IF NOT EXISTS library_item_status_history (
    id BIGSERIAL PRIMARY KEY,
    library_item_id BIGINT NOT NULL REFERENCES library_item(id) ON DELETE CASCADE,
    previous_status library_item_status,
    new_status library_item_status NOT NULL,
    transition_reason TEXT,
    transition_source VARCHAR(64) NOT NULL DEFAULT 'system', -- system|manual|api|worker
    payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_library_item_status_history_item_id ON library_item_status_history(library_item_id, created_at DESC);

-- Liaison entre les jobs existants et l'inventaire unifié.
ALTER TABLE processing_job
    ADD COLUMN IF NOT EXISTS library_item_id BIGINT REFERENCES library_item(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_processing_job_library_item_id ON processing_job(library_item_id);

-- Stockage centralisé des paramètres globaux de la zone "Configuration" (hors plugins).
CREATE TABLE IF NOT EXISTS app_configuration (
    id BIGSERIAL PRIMARY KEY,
    section VARCHAR(80) NOT NULL,
    config_key VARCHAR(120) NOT NULL,
    config_value JSONB NOT NULL,
    value_type VARCHAR(24) NOT NULL DEFAULT 'json', -- string|number|boolean|json|secret
    is_secret BOOLEAN NOT NULL DEFAULT FALSE,
    description TEXT,
    updated_by VARCHAR(120),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_app_configuration UNIQUE (section, config_key),
    CONSTRAINT ck_app_configuration_section_no_plugin_prefix
        CHECK (section NOT LIKE 'plugins.%')
);

CREATE INDEX IF NOT EXISTS idx_app_configuration_section ON app_configuration(section);

CREATE TABLE IF NOT EXISTS app_configuration_history (
    id BIGSERIAL PRIMARY KEY,
    configuration_id BIGINT NOT NULL REFERENCES app_configuration(id) ON DELETE CASCADE,
    previous_value JSONB,
    new_value JSONB NOT NULL,
    changed_by VARCHAR(120),
    change_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_app_configuration_history_configuration_id ON app_configuration_history(configuration_id, created_at DESC);

-- Registre des plugins installés: représentation "plugins > INSTALLED - discord".
CREATE TABLE IF NOT EXISTS plugin_registry (
    id BIGSERIAL PRIMARY KEY,
    plugin_code VARCHAR(80) NOT NULL UNIQUE, -- discord, telegram, email, ...
    display_name VARCHAR(120) NOT NULL,
    status plugin_install_status NOT NULL DEFAULT 'INSTALLED',
    version VARCHAR(40),
    has_html_page BOOLEAN NOT NULL DEFAULT TRUE,
    has_sql_migration BOOLEAN NOT NULL DEFAULT TRUE,
    has_python_module BOOLEAN NOT NULL DEFAULT TRUE,
    html_entrypoint TEXT,
    python_entrypoint TEXT,
    schema_name VARCHAR(120),
    installed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_plugin_registry_status ON plugin_registry(status);

-- Instances multi-config d'un plugin (ex: plusieurs webhooks Discord).
CREATE TABLE IF NOT EXISTS plugin_instance (
    id BIGSERIAL PRIMARY KEY,
    plugin_id BIGINT NOT NULL REFERENCES plugin_registry(id) ON DELETE CASCADE,
    instance_name VARCHAR(120) NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    priority INTEGER NOT NULL DEFAULT 100,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_plugin_instance UNIQUE (plugin_id, instance_name)
);

CREATE INDEX IF NOT EXISTS idx_plugin_instance_plugin_id_enabled ON plugin_instance(plugin_id, is_enabled);

-- Configuration spécialisée Discord (one-to-one avec plugin_instance).
CREATE TABLE IF NOT EXISTS plugin_discord_config (
    plugin_instance_id BIGINT PRIMARY KEY REFERENCES plugin_instance(id) ON DELETE CASCADE,
    webhook_url TEXT NOT NULL,
    channel_name VARCHAR(120),
    username_template VARCHAR(120),
    message_template TEXT,
    notify_on_success BOOLEAN NOT NULL DEFAULT TRUE,
    notify_on_error BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Configuration spécialisée Telegram.
CREATE TABLE IF NOT EXISTS plugin_telegram_config (
    plugin_instance_id BIGINT PRIMARY KEY REFERENCES plugin_instance(id) ON DELETE CASCADE,
    bot_token TEXT NOT NULL,
    chat_id VARCHAR(120) NOT NULL,
    parse_mode VARCHAR(20) NOT NULL DEFAULT 'HTML',
    notify_on_success BOOLEAN NOT NULL DEFAULT TRUE,
    notify_on_error BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Configuration spécialisée Email.
CREATE TABLE IF NOT EXISTS plugin_email_config (
    plugin_instance_id BIGINT PRIMARY KEY REFERENCES plugin_instance(id) ON DELETE CASCADE,
    smtp_host VARCHAR(255) NOT NULL,
    smtp_port INTEGER NOT NULL DEFAULT 587,
    smtp_username VARCHAR(255),
    smtp_password TEXT,
    smtp_tls BOOLEAN NOT NULL DEFAULT TRUE,
    from_address VARCHAR(255) NOT NULL,
    to_addresses TEXT[] NOT NULL,
    subject_template VARCHAR(255),
    notify_on_success BOOLEAN NOT NULL DEFAULT TRUE,
    notify_on_error BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMIT;
