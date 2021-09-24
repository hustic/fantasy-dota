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
                f'{base_url}/teams?api_key={api_key}').json()

        filtered = [r for r in resp if r['team_id'] in self.teams]

        self.default_db.load_data("logs_teams", filtered, replace=True)

        return self.success()
