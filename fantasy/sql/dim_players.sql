SELECT p.account_id
     , p.name
     , p.team_id
FROM logs_players AS p
JOIN dim_teams AS t
ON p.team_id = t.team_id

