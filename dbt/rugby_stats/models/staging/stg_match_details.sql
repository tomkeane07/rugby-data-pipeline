select
  cast(match_id as string) as match_id,
  cast(game_date as date) as game_date,
  cast(season as int64) as season,
  cast(competition_id as string) as competition_id,
  cast(competition_name as string) as competition_name
from {{ source('raw', 'match_details') }}
where match_id is not null
