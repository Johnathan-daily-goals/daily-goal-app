.PHONY: run test testv lint format db-psql

run:
	python -m backend.app.main

test:
	pytest -q

testv:
	pytest -vv

lint:
	python -m ruff check .

format:
	python -m ruff format .

db-psql:
	psql -U daily_user -d daily_goals_db