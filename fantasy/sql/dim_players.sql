SELECT p.account_id
     , r.role
  FROM logs_players AS p
  JOIN dim_teams AS t
    ON p.team_id = t.team_id
  JOIN logs_roles AS r
    ON r.name LIKE p.name

UNION

SELECT m.account_id
     , m.role
  FROM missing_players AS m
  JOIN logs_players AS p
    ON m.account_id = p.account_id