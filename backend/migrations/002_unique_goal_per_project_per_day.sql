CREATE UNIQUE INDEX IF NOT EXISTS daily_goals_unique_project_day
ON daily_goals (project_id, (DATE(created_at)));