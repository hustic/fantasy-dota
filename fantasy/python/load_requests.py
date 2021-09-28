import requests
import json
import time

from sayn import PythonTask
from pathos.helpers import cpu_count
from p_tqdm import p_umap


class LoadData(PythonTask):
    def setup(self):
        self.query = """
                SELECT match_id FROM logs_jobs GROUP BY match_id;
        """

        with open('player.json') as json_file:
            self.schema = json.load(json_file)

        return self.success()

    def run(self):

        base_url = self.parameters['base_url']
        api_key = self.parameters['api_key']

        match_ids = self.default_db.read_data(self.query)
        match_ids = [list(d.values())[0] for d in match_ids]

        def get_request(m, base_url, api_key, schema):
            response = requests.get(
                f"{base_url}/matches/{m}?api_key={api_key}").json()

            req_players = response['players']
            players = []
            for p in req_players:
                player = {}
                for key in schema.keys():
                    try:
                        player[f"{key}"] = p[f"{key}"]
                    except:
                        player[f"{key}"] = None
                players.append(player)
            return players

        data = p_umap(get_request, match_ids, [base_url for m in match_ids], [
                            api_key for m in match_ids], [self.schema for m in match_ids])

        data = [i for t in data for i in t]
        self.default_db.load_data(
            "logs_player_match_stats", data, replace=True, batch_size=500)

        return self.success()
