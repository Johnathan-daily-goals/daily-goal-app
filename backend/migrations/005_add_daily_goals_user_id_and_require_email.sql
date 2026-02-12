BEGIN;

-- 1) Require email on users
ALTER TABLE users
ALTER COLUMN email SET NOT NULL;

-- 2) Add user_id to daily_goals (nullable first so we can backfill)
ALTER TABLE daily_goals
ADD COLUMN IF NOT EXISTS user_id INTEGER;

-- 3) Backfill user_id from the owning project
UPDATE daily_goals dg
SET user_id = p.user_id
FROM projects p
WHERE dg.project_id = p.id
  AND dg.user_id IS NULL;

-- 4) Enforce NOT NULL after backfill
ALTER TABLE daily_goals
ALTER COLUMN user_id SET NOT NULL;

-- 5) Add FK + index
ALTER TABLE daily_goals
ADD CONSTRAINT daily_goals_user_id_fkey
FOREIGN KEY (user_id) REFERENCES users(id);

CREATE INDEX IF NOT EXISTS idx_daily_goals_user_id ON daily_goals(user_id);

COMMIT;