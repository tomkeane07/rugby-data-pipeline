# Rugby Stats Pipeline

End-to-end batch pipeline for rugby team performance analytics using rugbypy, BigQuery, dbt, Kestra, and Looker Studio.

## Project Goal

Build a reproducible data pipeline that:

1. Ingests team and team-game statistics.
2. Loads raw data into BigQuery.
3. Applies dbt transformations and tests.
4. Serves dashboard-ready metrics.

## Tech Stack

- Orchestration: Kestra (Docker Compose)
- Ingestion/Load: Python scripts in `scripts/`
- Warehouse: BigQuery
- Transformations: dbt (`dbt/rugby_stats`)
- Dashboard: Looker Studio

## Repository Structure

- `flows/rugby_pipeline_daily.yml`: Kestra flow (4 tasks)
- `scripts/`: ingestion, load, dbt execution, milestone utilities
- `dbt/rugby_stats/`: dbt project with staging/intermediate/marts and tests
- `docs/evidence/`: milestone evidence artifacts

## Prerequisites

1. Docker and Docker Compose
2. GCP service account key at `secrets/cloud_key.json`
3. Access to your target BigQuery project

## Configuration

1. Copy `.env.example` to `.env` and set your values.
2. Ensure `infra/terraform/terraform.tfvars` uses the same project and bucket naming convention.

## Reproduction Steps

Run from repository root.

Set environment variables first:

```bash
export GCP_PROJECT_ID=your-gcp-project-id
export BQ_DATASET_RAW=raw
export BQ_DATASET_ANALYTICS=raw
export GOOGLE_APPLICATION_CREDENTIALS=/workspace/secrets/cloud_key.json
```

1. Start Kestra stack:

```bash
docker compose -f docker-compose.kestra.yml up -d
```

2. Trigger the daily flow (UI or API):

- UI: `http://localhost:8080`
- Flow: `rugby.rugby_pipeline_daily`

3. Validate raw BigQuery tables (Milestone 4 utility):

```bash
docker run --rm \
  -v $PWD:/workspace \
  -w /workspace \
  -e GOOGLE_APPLICATION_CREDENTIALS=/workspace/secrets/cloud_key.json \
  -e GCP_PROJECT_ID=$GCP_PROJECT_ID \
  -e BQ_DATASET_RAW=$BQ_DATASET_RAW \
  rugby_data_project-python:latest \
  python scripts/milestone4_validate_bq.py
```

4. Validate dbt models/tests/docs (Milestone 5):

```bash
docker run --rm \
  -v $PWD:/workspace \
  -w /workspace \
  -e GOOGLE_APPLICATION_CREDENTIALS=/workspace/secrets/cloud_key.json \
  -e GCP_PROJECT_ID=$GCP_PROJECT_ID \
  -e BQ_DATASET_RAW=$BQ_DATASET_RAW \
  -e BQ_DATASET_ANALYTICS=$BQ_DATASET_ANALYTICS \
  rugby_data_project-python:latest \
  dbt build --project-dir dbt/rugby_stats --profiles-dir dbt/rugby_stats
```

5. Generate dashboard query/checklist pack (Milestone 6 utility):

```bash
docker run --rm \
  -v $PWD:/workspace \
  -w /workspace \
  -e GOOGLE_APPLICATION_CREDENTIALS=/workspace/secrets/cloud_key.json \
  -e GCP_PROJECT_ID=$GCP_PROJECT_ID \
  -e BQ_DATASET_RAW=$BQ_DATASET_RAW \
  rugby_data_project-python:latest \
  python scripts/milestone6_prepare_dashboard_evidence.py
```

## Evidence Map

- Milestone 1 (Terraform): `docs/evidence/milestone1/`
- Milestone 2 (Kestra flow + debugging): `docs/evidence/milestone2/`
- Milestone 4 (BigQuery load validation): `docs/evidence/milestone4/`
- Milestone 5 (dbt build/test/docs): `docs/evidence/milestone5/`
- Milestone 6 (Looker prep and checklist): `docs/evidence/milestone6/`
- Milestone 7 (reproducibility checklist/transcript): `docs/evidence/milestone7/`

## Notes

- Final successful orchestration run and fix history are summarized in `docs/evidence/milestone2/kestra_milestone2_rollup.md`.
- Dashboard screenshot capture remains a manual step in Looker Studio.
- New-project validation succeeded on `rugby-datatalks-pipeline` with a full successful rerun: `docs/evidence/milestone2/20260418T043007Z_new_project_full_rerun/rerun_summary.md`.
- Refreshed BigQuery/dbt evidence for the new project is in `docs/evidence/milestone4/20260418T043653Z/` and `docs/evidence/milestone5/20260418T043652Z_new_project_refresh/`.
