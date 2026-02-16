BEGIN;

DROP INDEX IF EXISTS daily_goals_unique_project_day;

CREATE UNIQUE INDEX daily_goals_unique_user_project_day
ON daily_goals (user_id, project_id, (date(created_at)));

COMMIT;