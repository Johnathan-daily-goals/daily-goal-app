-- 004_auth_users_and_project_owner.sql
-- Adds users + a simple token for dev auth, and makes projects owned by a user.

BEGIN;

-- For gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1) Users table (simple dev token-based auth)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE,
    token TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2) Create a default local dev user if none exists
INSERT INTO users (email, token)
SELECT 'local-dev@example.com', gen_random_uuid()::text
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'local-dev@example.com');

-- 3) Add ownership to projects
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS user_id INTEGER;

-- 4) Backfill existing projects to the default user
UPDATE projects
SET user_id = (SELECT id FROM users WHERE email = 'local-dev@example.com')
WHERE user_id IS NULL;

-- 5) Enforce ownership
ALTER TABLE projects
ALTER COLUMN user_id SET NOT NULL;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'projects_user_id_fkey'
  ) THEN
    ALTER TABLE projects
      ADD CONSTRAINT projects_user_id_fkey
      FOREIGN KEY (user_id) REFERENCES users(id);
  END IF;
END $$;

-- Helpful index
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);

COMMIT;