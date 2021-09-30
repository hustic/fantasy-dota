import requests
from pathlib import Path
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

        self.set_run_steps(
            [
                "Get match_ids from DB",
                "Get match details",
                "Format Output & get Timeseries data",
                "Save Timeseries data",
                "Load Player Match Stats"
            ]
        )

        with self.step("Get match_ids from DB"):
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

        with self.step("Get match details"):
            data = p_umap(get_request, match_ids, [base_url for m in match_ids], [
                            api_key for m in match_ids], [self.schema for m in match_ids])

        with self.step("Format Output & get Timeseries data"):
            final = []
            timeseries = []
            for dat in data:
                for d in dat:
                    ts = {"account_id": d["account_id"], "match_id": d["match_id"],
                          "gold_t": d["gold_t"], "xp_t": d["xp_t"], "lh_t": d["lh_t"], "dn_t": d["dn_t"]}
                    timeseries.append(ts)
                    del d["gold_t"]
                    del d["xp_t"]
                    del d["lh_t"]
                    del d["dn_t"]
                    final.append(d)

        with self.step("Save Timeseries data"):
            file = Path('./timeseries/match_data.json')
            with open(file, 'w') as f:
                json.dump(timeseries, f, indent=2)

        with self.step("Load Player Match Stats"):
            self.default_db.load_data(
                "logs_player_match_stats", final, replace=True, batch_size=500)

        return self.success()
