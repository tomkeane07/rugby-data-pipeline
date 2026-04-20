# Inspecting `fct_team_performance` Schema

This page shows how to print the table structure for `fct_team_performance` so you can quickly discover available columns for new analyses and dashboard ideas.

## Option 1: BigQuery INFORMATION_SCHEMA (recommended)

Run this query in BigQuery (Console or `bq query`) to print column names, types, nullability, and ordinal position.

```sql
select
  ordinal_position,
  column_name,
  data_type,
  is_nullable
from `rugby-datatalks-pipeline.raw.INFORMATION_SCHEMA.COLUMNS`
where table_name = 'fct_team_performance'
order by ordinal_position;
```

This is the cleanest view for schema discovery and is easy to copy into documentation.

## Option 2: BigQuery table metadata (CLI)

If you use the `bq` CLI, this prints full table metadata including schema.

```bash
bq show --format=prettyjson rugby-datatalks-pipeline:raw.fct_team_performance
```

To print only column names and types from the JSON output:

```bash
bq show --format=prettyjson rugby-datatalks-pipeline:raw.fct_team_performance \
  | jq -r '.schema.fields[] | "\(.name)\t\(.type)\t\(.mode)"'
```

## Option 3: Python snippet in project container

This is useful if you already run commands via Docker in this project.

```bash
docker compose run --rm python python - <<'PY'
from google.cloud import bigquery

client = bigquery.Client(project='rugby-datatalks-pipeline')
table = client.get_table('rugby-datatalks-pipeline.raw.fct_team_performance')

print('name\ttype\tmode')
for f in table.schema:
    print(f'{f.name}\t{f.field_type}\t{f.mode}')
PY
```

## Current Model Columns

Based on [dbt/rugby_stats/models/marts/fct_team_performance.sql](../../../dbt/rugby_stats/models/marts/fct_team_performance.sql), the model currently selects:

1. `team_game_key`
2. `team_id`
3. `team_name`
4. `match_id`
5. `game_date`
6. `season`
7. `competition_id`
8. `competition_name`
9. `opponent_team_id`
10. `opponent_team_name`
11. `tries`
12. `line_breaks`
13. `entries_22m`
14. `territory`
15. `score`
16. `opponent_score`
17. `score_difference`
18. `winner_flag`
19. `tries_rolling_5`
20. `line_breaks_rolling_5`
21. `territory_rolling_5`

## Tip for Future Graph Ideas

For rapid exploration, start with:

```sql
select *
from `rugby-datatalks-pipeline.raw.fct_team_performance`
limit 50;
```

Then narrow to relevant columns and aggregate at the target graph grain.
