# Testing Guide

This project includes a lightweight smoke test suite for fast local validation of helper logic used by ingestion and BigQuery load scripts.

## Scope

Current smoke tests focus on pure helper functions (non-network):

- `scripts/ingest_rugby_data.py`
- `scripts/load_to_bigquery.py`

Test files:

- `tests/smoke/test_ingest_helpers.py`
- `tests/smoke/test_load_helpers.py`

## Run Tests

Preferred command:

```bash
make test-smoke
```

This runs pytest in the project container with the correct Python path:

- `docker compose run --rm python sh -lc "PYTHONPATH=/workspace pytest -q tests/smoke"`

## What Passing Means

When tests pass, you have confirmation that:

1. Ingestion helper parsing behaves as expected.
2. BigQuery load helper functions (file selection and object normalization) behave as expected.

These checks are intended as a fast preflight before slower end-to-end pipeline runs.

## Suggested Workflow

1. `make test-smoke`
2. `make pipeline-local` (optional full run)
3. `make dbt-build` for model/test validation
