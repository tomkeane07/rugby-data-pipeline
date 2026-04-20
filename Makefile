.PHONY: help build kestra-up kestra-down kestra-logs fetch-teams fetch-team-stats fetch-match-details ingest-all load-bq dbt-build dbt-test validate-bq dashboard-evidence test-smoke pipeline-local

COMPOSE = docker compose
PYTHON = $(COMPOSE) run --rm python

help:
	@echo "Available targets:"
	@echo "  make build               Build the python service image"
	@echo "  make kestra-up           Start Kestra + Postgres stack"
	@echo "  make kestra-down         Stop Kestra + Postgres stack"
	@echo "  make kestra-logs         Tail Kestra logs"
	@echo "  make fetch-teams         Fetch teams to data/raw/teams"
	@echo "  make fetch-team-stats    Fetch team stats to data/raw/team_stats"
	@echo "  make fetch-match-details Fetch match metadata to data/raw/match_details"
	@echo "  make ingest-all          Run all three fetch steps"
	@echo "  make load-bq             Load raw parquet files into BigQuery raw tables"
	@echo "  make dbt-build           Run dbt build + dbt test via scripts/run_dbt.py"
	@echo "  make dbt-test            Run dbt test directly"
	@echo "  make validate-bq         Validate raw BigQuery tables (milestone 4)"
	@echo "  make dashboard-evidence  Prepare dashboard evidence artifacts (milestone 6)"
	@echo "  make test-smoke          Run fast non-network smoke tests"
	@echo "  make pipeline-local      ingest-all -> load-bq -> dbt-build"

build:
	$(COMPOSE) build python

kestra-up:
	$(COMPOSE) -f docker-compose.kestra.yml up -d

kestra-down:
	$(COMPOSE) -f docker-compose.kestra.yml down

kestra-logs:
	$(COMPOSE) -f docker-compose.kestra.yml logs -f kestra

fetch-teams:
	$(PYTHON) python scripts/fetch_teams.py

fetch-team-stats:
	$(PYTHON) python scripts/fetch_team_stats.py

fetch-match-details:
	$(PYTHON) python scripts/fetch_match_details.py

ingest-all: fetch-teams fetch-team-stats fetch-match-details

load-bq:
	$(PYTHON) python scripts/load_to_bigquery.py

dbt-build:
	$(PYTHON) python scripts/run_dbt.py

dbt-test:
	$(PYTHON) dbt test --project-dir dbt/rugby_stats --profiles-dir dbt/rugby_stats

validate-bq:
	$(PYTHON) python scripts/milestone4_validate_bq.py

dashboard-evidence:
	$(PYTHON) python scripts/milestone6_prepare_dashboard_evidence.py

test-smoke:
	$(PYTHON) sh -lc "PYTHONPATH=/workspace pytest -q tests/smoke"

pipeline-local: ingest-all load-bq dbt-build
