BEGIN;

ALTER TABLE users
ADD COLUMN IF NOT EXISTS token_expires_at TIMESTAMP WITHOUT TIME ZONE;

UPDATE users
SET token_expires_at = COALESCE(token_expires_at, CURRENT_TIMESTAMP + INTERVAL '1 day');

ALTER TABLE users
ALTER COLUMN token_expires_at SET NOT NULL;

CREATE INDEX IF NOT EXISTS idx_users_token_expires_at ON users (token_expires_at);

COMMIT;