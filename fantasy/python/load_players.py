import requests

from sayn import PythonTask


class LoadData(PythonTask):
    # Dimensions
    teams = [15, 39, 1883502, 7390454, 5, 8214850, 8255756, 2586976, 7119388,
             726228, 1838315, 6209166, 111474, 8254400, 7391077, 8260983, 8204512, 350190]

    def run(self):

        base_url = self.parameters['base_url']
        api_key = self.parameters['api_key']

        resp = requests.get(
                    f'{base_url}/proPlayers?api_key={api_key}').json()

        keys_to_drop = ['steamid', 'avatar', 'avatarmedium', 'avatarfull',
                        'profileurl', 'personaname', 'last_login', 'full_history_time',
                        'cheese', 'fh_unavailable', 'loccountrycode', 'last_match_time',
                        'plus', 'country_code', 'team_name', 'locked_until', 'is_locked', 'is_pro']
        data = []
        for r in resp:
            for key in keys_to_drop:
                r.pop(key, None)
            data.append(r)

        self.default_db.load_data(
            "logs_players", data, replace=True)

        return self.success()
