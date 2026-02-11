-- create_tables.sql

CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    date_created DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS daily_goals (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    goal_text TEXT NOT NULL,
    date_created DATE NOT NULL DEFAULT CURRENT_DATE
);