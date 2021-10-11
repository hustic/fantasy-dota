SELECT lm.match_id
     , lm.radiant_team_id
     , lm.dire_team_id
     , lm.series_id
     , lm.series_type
     , lm.radiant_win
     , lm.leagueid
  FROM logs_matches AS lm
  JOIN dim_teams AS t
    ON lm.radiant_team_id = t.team_id
 WHERE lm.start_time > strftime('%s', '{{ date }}' )

UNION

SELECT lm.match_id
     , lm.radiant_team_id
     , lm.dire_team_id
     , lm.series_id
     , lm.series_type
     , lm.radiant_win
     , lm.leagueid
  FROM logs_matches AS lm
  JOIN dim_teams AS t
    ON lm.dire_team_id = t.team_id
 WHERE lm.start_time > strftime('%s', '{{ date }}' )
