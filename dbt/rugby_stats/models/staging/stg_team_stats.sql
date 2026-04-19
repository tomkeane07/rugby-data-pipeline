with base as (
  select
    cast(team_id as string) as team_id,
    cast(team as string) as team_name,
    cast(match_id as string) as match_id,
    cast(team_vs_id as string) as opponent_team_id,
    cast(team_vs as string) as opponent_team_name,
    cast(game_date as date) as game_date,
    extract(year from cast(game_date as date)) as season,
    cast(tries as float64) as tries,
    cast(line_breaks as float64) as line_breaks,
    cast(`22m_entries` as float64) as entries_22m,
    cast(territory as float64) as territory,
    cast(score as float64) as score,
    cast(team_vs_score as float64) as opponent_score
  from {{ source('raw', 'team_stats') }}
  where game_date is not null
    and team_id is not null
    and match_id is not null
)
select
  concat(team_id, '-', match_id) as team_game_key,
  team_id,
  team_name,
  match_id,
  opponent_team_id,
  opponent_team_name,
  game_date,
  season,
  tries,
  line_breaks,
  entries_22m,
  territory,
  score,
  opponent_score
from base
qualify row_number() over (
  partition by team_id, match_id
  order by game_date desc
) = 1
