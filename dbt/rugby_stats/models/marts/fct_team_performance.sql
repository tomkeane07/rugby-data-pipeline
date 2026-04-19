select
  m.team_game_key,
  m.team_id,
  m.team_name,
  m.match_id,
  m.game_date,
  m.season,
  m.competition_id,
  m.competition_name,
  m.opponent_team_id,
  m.opponent_team_name,
  m.tries,
  m.line_breaks,
  m.entries_22m,
  m.territory,
  m.score,
  m.opponent_score,
  m.score_difference,
  m.winner_flag,
  avg(m.tries) over (
    partition by m.team_id
    order by m.game_date
    rows between 4 preceding and current row
  ) as tries_rolling_5,
  avg(m.line_breaks) over (
    partition by m.team_id
    order by m.game_date
    rows between 4 preceding and current row
  ) as line_breaks_rolling_5,
  avg(m.territory) over (
    partition by m.team_id
    order by m.game_date
    rows between 4 preceding and current row
  ) as territory_rolling_5
from {{ ref('int_team_game_metrics') }} m
