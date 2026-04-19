select
  s.team_game_key,
  s.team_id,
  s.team_name,
  s.opponent_team_id,
  s.opponent_team_name,
  s.match_id,
  s.game_date,
  s.season,
  d.competition_id,
  d.competition_name,
  s.tries,
  s.line_breaks,
  s.entries_22m,
  s.territory,
  s.score,
  s.opponent_score,
  (s.score - s.opponent_score) as score_difference,
  case
    when s.score > s.opponent_score then 'W'
    when s.score < s.opponent_score then 'L'
    else 'D'
  end as winner_flag
from {{ ref('stg_team_stats') }} s
left join {{ ref('stg_match_details') }} d
  on s.match_id = d.match_id
