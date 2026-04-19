# Rugby Team Performance Dashboard — Project Roadmap

## Problem Statement

Rugby analytics data is hard to access and visualise in aggregate. This project builds an end-to-end batch data pipeline using the `rugbypy` Python package to ingest team performance statistics across the 2022–2025 seasons, store them in a cloud data warehouse, and expose insights via an interactive dashboard. The dashboard will help analysts and fans understand how team performance metrics (tries, line breaks, territory) vary across competitions and evolve over time.

---

## Architecture Overview

```
rugbypy API → Python ingestion script → GCS (data lake)
                                             ↓
                                       BigQuery (data warehouse)
                                             ↓
                                        dbt (transformations)
                                             ↓
                Looker Studio (dashboard)
```

---

## Technology Choices

| Layer | Tool | Reason |
|---|---|---|
| Cloud | GCP | BigQuery + GCS integrate natively |
| IaC | Terraform | Provision GCS bucket + BigQuery dataset |
| Orchestration | Kestra (local Docker Compose) | YAML-based scheduling pattern already proven in prior modules |
| Data Lake | GCS | Parquet files partitioned by ingestion date |
| Data Warehouse | BigQuery | Serverless, partitioning/clustering support |
| Transformations | dbt | SQL models with lineage and testing |
| Dashboard | Looker Studio | Free, connects directly to BigQuery |

---

## Decision Log (Locked)

The following decisions close open options using patterns already proven in completed DataTalks modules. Where earlier sections list alternatives, this log is the source of truth.

| Decision Area | Final Choice | Rationale from completed work | Done When |
|---|---|---|---|
| Dashboard | Looker Studio (primary) | Existing warehouse-first workflow and direct BigQuery connectivity keep delivery simple | Two required tiles are published and filter correctly by team and season |
| Orchestration | Kestra on Docker Compose (local) | Module 2 already uses parameterized YAML flows and scheduler patterns | Daily flow runs end-to-end with 4 tasks and logs are visible in UI |
| IaC | Terraform + remote state in GCS | Module 1 established Terraform workflow; remote state improves reproducibility | `terraform apply` creates bucket + dataset and state is stored in backend bucket |
| Runtime | Docker Compose + Makefile commands | Repeated pattern across modules for reproducible local setup | `make up`, `make down`, and pipeline targets work from clean checkout |
| Ingestion strategy | Daily incremental append + weekly reconciliation run | Better cost/runtime than full refresh while still correcting late updates | Daily job only loads new/changed games; weekly job detects and fixes drift |
| Idempotency key | `team_id + game_id` (or equivalent stable game key) | Needed to prevent duplicate team-game rows across reruns | Merge/upsert logic keeps one canonical row per team-game |
| API resilience | Retries with exponential backoff, bounded concurrency, per-team error capture | Aligns with prior parallel ingestion patterns while handling transient failures | Temporary API failures recover automatically; failed teams are retried and reported |
| Data lake format | Parquet + Snappy, partitioned by `ingestion_date` | Matches existing parquet-centric ingestion and efficient load patterns | Files land under date partitions and are queryable/loadable without schema breakage |
| BigQuery raw design | Partition by `game_date`, cluster by `team_id` | Matches planned dashboard filters and group-by access patterns | Query plan shows partition pruning and reduced scanned bytes on date/team filters |
| BigQuery load method | Batch load jobs from GCS parquet into `raw.*` | Stable and reproducible pattern for warehouse ingestion | Load task completes with audited row counts and deterministic schema mapping |
| dbt architecture | `staging -> intermediate -> marts` | Module 4 project structure already follows this convention | dbt graph shows 3-layer lineage and builds successfully in dev/prod targets |
| dbt tests | `not_null`, `unique`, `relationships`, `accepted_values` | Extends existing dbt generic test usage with domain checks | `dbt test` passes on key identifiers and core metric fields |
| Secrets | `.env` + mounted service account key, never committed | Matches existing local/cloud credential workflow | Repo has no credential files tracked; runtime auth works via env vars |
| Monitoring baseline | Kestra run status + freshness/row-count checks | Practical observability baseline without adding new platforms | Failed runs are visible, and daily data freshness check alerts on stale loads |

---

## Data Ingestion

**Type**: Batch (daily)

**Source endpoints used**:
- `fetch_all_teams()` — get all ~289 team IDs
- `fetch_team_stats(team_id)` — get all game-level stats per team

**DAG steps**:
1. `fetch_teams` — pull team registry, write to GCS as `teams.parquet`
2. `fetch_team_stats` — loop over all team IDs, write each to GCS as `team_stats/{team_id}.parquet`
3. `load_to_bigquery` — load Parquet files from GCS into raw BigQuery tables
4. `run_dbt` — trigger dbt transformations

**Schedule**: Daily (new matches appear regularly during season)

---

## Data Lake (GCS)

**Bucket structure**:
```
gs://rugby-data-lake/
  raw/
    teams/
      teams_YYYYMMDD.parquet
    team_stats/
      {team_id}_YYYYMMDD.parquet
```

---

## Data Warehouse (BigQuery)

**Raw tables**:
- `raw.teams` — team_id, team_name
- `raw.team_stats` — all 59 columns from `fetch_team_stats`

**Optimisation**:
- `raw.team_stats` partitioned by `game_date` (date column) — dashboard queries filter by season/date range
- `raw.team_stats` clustered by `team_id` — most queries filter or group by team

---

## Transformations (dbt)

**Models**:

`stg_team_stats.sql` — clean and cast raw stats, filter out null game dates

`dim_teams.sql` — deduplicated team reference table

`fct_team_performance.sql` — one row per team per game, with:
- `tries`, `line_breaks`, `22m_entries`, `territory`
- `game_date`, `season` (extracted from date), `competition` (via join if available)
- rolling 5-game averages for key metrics

---

## Dashboard (Looker Studio)

**Tile 1 — Temporal**: Line chart of average tries/line breaks per game month across the 2022–2025 seasons, filterable by team.

**Tile 2 — Categorical**: Bar chart of average territory % and 22m entries grouped by team, filterable by season.

---

## Milestones

| # | Task | Notes |
|---|---|---|
| 1 | Terraform: provision GCS + BigQuery | IaC for full marks |
| 2 | Write ingestion script + test locally | Use notebook to validate |
| 3 | Build Kestra flow with all 4 steps | End-to-end for full marks |
| 4 | Load raw data into BigQuery with partitioning | Explain partition strategy in README |
| 5 | Write dbt models + tests | `not_null`, `unique` tests on key fields |
| 6 | Build Looker Studio dashboard | 2 tiles for full marks |
| 7 | Write README with full reproduction steps | Required for reproducibility marks |
| 8 | (Optional) Add CI/CD + Make | Portfolio quality |

## Current Status (April 18, 2026)

| Milestone | Status | Evidence |
|---|---|---|
| 1. Terraform: provision GCS + BigQuery | Complete | `docs/evidence/milestone1/` |
| 2. Ingestion script + local test | Complete | `docs/evidence/milestone2/ingest_run.log`, `docs/evidence/milestone2/output_file_listing.txt` |
| 3. Kestra flow with 4 steps | Complete | `docs/evidence/milestone2/20260418T043007Z_new_project_full_rerun/rerun_summary.md` |
| 4. Load raw data to BigQuery | Complete | `docs/evidence/milestone4/20260418T043653Z/milestone4_validation.md` |
| 5. dbt models + tests | Complete | `docs/evidence/milestone5/20260418T043652Z_new_project_refresh/milestone5_summary.md` |
| 6. Looker Studio dashboard | In progress (awaiting manual screenshots/URL capture) | `docs/evidence/milestone6/20260418T034814Z/milestone6_dashboard_checklist.md` |
| 7. Reproducible README | Complete | `README.md`, `docs/evidence/milestone7/reproducibility_checklist.md`, `docs/evidence/milestone7/command_transcript.md` |

### Migration Update (New GCP Project)

- Active project is now `rugby-datatalks-pipeline`.
- End-to-end Kestra rerun on the new project succeeded with all tasks `SUCCESS`.
- Milestone 4 and 5 evidence were refreshed against the new project environment.

Phase 1 is ready for submission once Milestone 6 screenshot evidence and dashboard URL are recorded.

---

## Phase 1 Acceptance Checklist

Use this checklist as the final gate before submission.

| Milestone | Acceptance Criteria | Validation Method | Evidence Artifact |
|---|---|---|---|
| 1. Terraform: provision GCS + BigQuery | Bucket and dataset are created by IaC with no manual console steps | Run `terraform plan` then `terraform apply` from clean state | Terraform output log + state backend config |
| 2. Ingestion script + local test | Teams and team stats ingestion completes locally without runtime errors | Execute ingestion entrypoint and confirm output parquet files are produced | Local run log + sample output file listing |
| 3. Kestra flow with 4 steps | Daily flow executes all tasks: fetch teams, fetch stats, load raw, run dbt | Trigger flow manually and verify all task statuses are `SUCCESS` | Kestra execution screenshot/export |
| 4. Load raw data to BigQuery | Raw tables exist, contain records, and are partitioned/clustering as defined | Run table metadata query and row count checks in BigQuery | Query results showing schema + partition/clustering + counts |
| 5. dbt models + tests | dbt build succeeds and tests pass for key fields and relationships | Run `dbt build` and `dbt test` on target profile | dbt CLI output + generated docs lineage screenshot |
| 6. Looker Studio dashboard | Dashboard includes both required tiles with functioning team/season filters | Open dashboard, apply filters, and verify chart updates | Dashboard URL + screenshots of both filtered views |
| 7. Reproducible README | A new user can reproduce setup and run order end-to-end using documented commands | Follow README in fresh environment and record run order/results | README checklist tick-off + command transcript |

Submission rule: mark Phase 1 complete only when Milestones 1-7 each have stored evidence.

---

## Out of Scope / Deferred (Phase 2)

The items below are intentionally deferred to keep Phase 1 focused on a reliable end-to-end batch pipeline.

| Area | Deferred Item | Why Deferred | Revisit Trigger |
|---|---|---|---|
| CI/CD | Automated checks and deployment pipeline (e.g., lint/test/dbt in PR) | Not required for MVP grading criteria | Core pipeline is stable for 2+ weeks and repo is portfolio-ready |
| Monitoring | Alert routing (email/Slack/webhook) and richer observability | Baseline run-status + freshness checks are sufficient for MVP | More than one operator depends on daily runs |
| Data Quality | Advanced anomaly detection beyond dbt generic tests | Initial quality gates cover schema and key constraints | Dashboard consumers request SLA-backed quality reporting |
| Cost Management | Automated cost guardrails and budget alerting | Early volumes are expected to be low | Monthly query/storage spend exceeds project budget threshold |
| Security Hardening | Secret manager integration and stricter IAM role split | `.env` + service account is acceptable for local/project scope | Transition to shared/team environment |
| Orchestration Platform | Migration from local Kestra to managed orchestration | Local Compose setup is faster to implement and reproduce | Reliability or scheduling requirements exceed local runtime |

---

## Repository Name Suggestion

`rugby-performance-analytics` or `rugby-stats-pipeline`