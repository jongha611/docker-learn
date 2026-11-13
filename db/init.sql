CREATE TABLE IF NOT EXISTS links (
    code       VARCHAR(16) PRIMARY KEY,
    url        TEXT        NOT NULL,
    clicks     INTEGER     NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

