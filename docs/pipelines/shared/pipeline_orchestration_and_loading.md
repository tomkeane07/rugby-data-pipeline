# Shared Component: Pipeline Orchestration and Loading

This page describes the shared upstream pipeline components used by both dashboard graphs.

## Visual Overview

```mermaid
flowchart TD
	classDef source fill:#f3efe2,stroke:#7a5c2e,color:#2f2416,stroke-width:1px;
	classDef ingest fill:#d9ead3,stroke:#4f7a52,color:#1f3b21,stroke-width:1px;
	classDef raw fill:#dbe7f7,stroke:#4f6b8a,color:#1d2d44,stroke-width:1px;
	classDef transform fill:#fde7c8,stroke:#b7791f,color:#4a2b00,stroke-width:1px;
	classDef serve fill:#f7d9d9,stroke:#9b4d4d,color:#4a1f1f,stroke-width:1px;

	A[rugbypy API] --> B[fetch_teams]
	A --> C[fetch_team_stats]
	A --> D[fetch_match_details]
	B --> E[data/raw/teams/*.parquet]
	C --> F[data/raw/team_stats/*.parquet]
	D --> G[data/raw/match_details/*.parquet]
	E --> H[load_to_bigquery.py]
	F --> H
	G --> H
	H --> I[BigQuery raw.teams]
	H --> J[BigQuery raw.team_stats]
	H --> K[BigQuery raw.match_details]
	I --> L[dbt build + test]
	J --> L
	K --> L
	L --> M[fct_team_performance]
	M --> N[vw_league_margin_categorical]
	M --> O[vw_league_score_difference_timeseries]
	N --> P[Looker Studio categorical graph]
	O --> Q[Looker Studio timeseries graph]

	class A source;
	class B,C,D,H,L ingest;
	class E,F,G,I,J,K raw;
	class M,N,O transform;
	class P,Q serve;
```

Character sketch of the same flow:

```text
rugbypy API
	|
	+--> fetch_teams ----------> data/raw/teams/*.parquet ---------
	|                                                           |
	+--> fetch_team_stats -----> data/raw/team_stats/*.parquet   +--> load_to_bigquery.py
	|                                                           |         |
	+--> fetch_match_details -> data/raw/match_details/*.parquet --------+
																	  |
																	  v
															BigQuery raw tables
																	  |
																	  v
																dbt build + test
																	  |
																	  v
															fct_team_performance
															  /                \
															 v                  v
									vw_league_margin_categorical   vw_league_score_difference_timeseries
															 |                  |
															 v                  v
											   categorical graph     timeseries graph
```

## Purpose

Both graphs depend on the same batch pipeline stages:

1. Extract rugby data from the `rugbypy` package into local parquet files.
2. Load those parquet files into BigQuery raw tables.
3. Run dbt models and tests to publish dashboard-ready views.

The graph-specific marts diverge only after the shared fact model is built.

## Orchestration Layer

The end-to-end job is orchestrated by Kestra in [flows/rugby_pipeline_daily.yml](../../../flows/rugby_pipeline_daily.yml).

The flow runs five tasks in order:

1. `fetch_teams`
2. `fetch_team_stats`
3. `fetch_match_details`
4. `load_to_bigquery`
5. `run_dbt`

This sequencing matters because downstream steps assume that fresh raw parquet files and raw BigQuery tables already exist.

## Extraction Scripts

The main shared extraction logic lives in [scripts/ingest_rugby_data.py](../../../scripts/ingest_rugby_data.py), with Kestra invoking the narrower task-specific scripts for teams, team stats, and match details.

Key behaviours in the ingestion pattern:

- Team metadata is fetched first so later tasks have a current list of `team_id` values.
- Team stats are written to `data/raw/team_stats/*.parquet`.
- Run summaries are written to `data/raw/run_summaries/` for traceability.
- Failures are recorded rather than silently discarded.

This raw-zone design keeps the extraction stage simple and auditable. It also allows the warehouse load step to be re-run without having to call the source API again.

## Raw BigQuery Load

The warehouse load step is implemented in [scripts/load_to_bigquery.py](../../../scripts/load_to_bigquery.py).

It loads three raw tables:

- `raw.teams`
- `raw.team_stats`
- `raw.match_details`

Important implementation details:

- `teams` loads from the latest `teams_*.parquet` snapshot.
- `team_stats` loads by concatenating all files in `data/raw/team_stats/*.parquet`.
- `match_details` loads from the latest `match_details_*.parquet` snapshot to avoid duplicate `match_id` values across historical snapshot files.
- Object columns containing lists or dictionaries are JSON-serialized so BigQuery receives scalar-compatible values.
- `game_date` is normalized to a date type before loading.
- `raw.team_stats` is partitioned by `game_date` and clustered by `team_id`.
- `raw.match_details` is partitioned by `game_date` and clustered by `competition_id`.

These storage choices directly support the dashboard workload, which commonly filters by date range, competition, and team.

## dbt Build Step

The transformation step is launched by [scripts/run_dbt.py](../../../scripts/run_dbt.py).

The script runs:

1. `dbt build`
2. `dbt test`

If `dbt build` fails, tests are not treated as valid and the script exits with a non-zero status. This is important operationally because both dashboard graphs should only be refreshed from validated transformation outputs.

## Dependency Boundary

Both graphs share everything on this page. Their logic only starts to differ after dbt publishes the shared fact model documented in [Fact Model and Data Quality Guards](./fact_model_and_quality_guards.md).
