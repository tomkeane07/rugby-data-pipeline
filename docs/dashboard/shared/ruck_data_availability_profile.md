# Ruck Data Availability Profile

This note captures the current availability of ruck-related fields in raw team stats and provides a repeatable way to refresh the profile.

## Why This Is Stored Separately

Ruck fields are relevant for future feature development, but coverage is incomplete and varies by file. Keeping this as a dedicated profile note makes that constraint visible before adding new models, tests, or dashboard tiles.

## Current Snapshot

Snapshot date: 2026-04-20

Source scanned:

- `data/raw/team_stats/*.parquet`
- Total files scanned: `213`

Detected ruck-related columns:

- `ruck_speed_0_3_pct`
- `ruck_speed_3_6_pct`
- `ruck_speed_6_plus_pct`
- `rucks_won`
- `rucks_total`

Coverage and non-null profile:

| Column | Files with column | Non-null rows / rows where column exists | Non-null % |
|---|---:|---:|---:|
| `ruck_speed_0_3_pct` | 158 / 213 | 6939 / 8774 | 79.1% |
| `ruck_speed_3_6_pct` | 158 / 213 | 6939 / 8774 | 79.1% |
| `ruck_speed_6_plus_pct` | 158 / 213 | 6939 / 8774 | 79.1% |
| `rucks_won` | 176 / 213 | 8387 / 8936 | 93.9% |
| `rucks_total` | 119 / 213 | 3596 / 7128 | 50.4% |

## Interpretation for Development

- `rucks_won` is the most reliable ruck field in current raw history.
- Ruck-speed fields are moderately complete and may require date/league filtering for stable analytics.
- `rucks_total` is sparse enough that it should not be assumed available by default.
- These fields are currently not selected in the active dbt staging/fact pipeline, so downstream marts do not expose them yet.

## Refresh Procedure

Use this command to regenerate the same profile in the project container environment:

```bash
cd /home/tomkeane/projects/rugby_data_project && docker compose run --rm python python - <<'PY'
from pathlib import Path
import pandas as pd

files = sorted(Path('data/raw/team_stats').glob('*.parquet'))
cols = ['ruck_speed_0_3_pct','ruck_speed_3_6_pct','ruck_speed_6_plus_pct','rucks_won','rucks_total']

presence = {c: 0 for c in cols}
rows_total = {c: 0 for c in cols}
rows_non_null = {c: 0 for c in cols}

for f in files:
    df = pd.read_parquet(f)
    n = len(df)
    for c in cols:
        if c in df.columns:
            presence[c] += 1
            rows_total[c] += n
            rows_non_null[c] += int(df[c].notna().sum())

print(f'total_files={len(files)}')
for c in cols:
    p = presence[c]
    if rows_total[c] == 0:
        print(f'{c}: files_with_column={p}/{len(files)} row_non_null=0/0')
    else:
        pct = 100.0 * rows_non_null[c] / rows_total[c]
        print(f'{c}: files_with_column={p}/{len(files)} row_non_null={rows_non_null[c]}/{rows_total[c]} ({pct:.1f}%)')
PY
```

After re-running, update this file's snapshot date and metrics.
