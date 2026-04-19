{{ config(materialized='view') }}

with base as (
  select
    match_id,
    game_date,
    team_name,
    opponent_team_name,
    score_difference,
    competition_id,
    competition_name
  from {{ ref('fct_team_performance') }}
),
match_labels as (
  select
    match_id,
    min(team_name) as team_name_a,
    max(team_name) as team_name_b
  from base
  group by match_id
),
league_mapped as (
  select
    b.match_id,
    game_date,
    b.team_name,
    b.opponent_team_name,
    b.score_difference,
    b.competition_id,
    b.competition_name,
    concat(cast(game_date as string), ' | ', ml.team_name_a, ' vs ', ml.team_name_b) as match_label,
    case
      when b.competition_id = '83d92007' then 'European Rugby Challenge Cup'
      when b.competition_id = 'ee0c6883' then 'European Rugby Champions Cup'
      when lower(b.competition_name) = 'major league rugby' then 'Major League Rugby'
      when lower(b.competition_name) in ('super rugby pacific', 'super rugby')
        or b.competition_id = '877aa127' then 'Super Rugby Pacific'
      else null
    end as league_name
  from base b
  left join match_labels ml
    on b.match_id = ml.match_id
)
select
  match_id,
  match_label,
  game_date,
  team_name,
  opponent_team_name,
  score_difference,
  competition_id,
  competition_name,
  league_name
from league_mapped
where league_name is not null
