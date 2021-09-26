import requests
import json

from sayn import PythonTask


class LoadData(PythonTask):

    def setup(self):
        self.query = """
                SELECT match_id FROM dim_matches GROUP BY match_id;
        """
        return self.success()

    def run(self):

        base_url = self.parameters['base_url']
        api_key = self.parameters['api_key']

        
        match_ids = self.default_db.read_data(self.query)
        match_ids = [ list(d.values())[0] for d in match_ids]

        print(match_ids[:1])


        # jobs = [requests.post(f'{base_url}/request/{m}?api_key={api_key}').json()['job']['jobId'] for m in match_ids[:1]]
        jobs = [155900072]
        print(jobs)     

        resp = [requests.get(f'{base_url}/request/{j}?api_key={api_key}').json()  for j in jobs] 

        print(resp)
        # self.set_run_steps(
        #     [
        #         "Get from API",
        #         "Filter",
        #         "Drop Columns",
        #         f"Load {name}",
        #     ]
        # )
        response = requests.get(f"{base_url}/matches/{match_ids[:1][0]}").json()
        print(response)
        # response

        with open('match_details.json', 'w') as f:
            json.dump(response, f, indent = 2)
        # with self.step("Get from API"):
        #     resp = requests.get(
        #             f'{base_url}/{api_call}?api_key={api_key}').json()

        # with self.step('Drop Columns'):
        #     data = []
        #     for r in resp:
        #         for key in keys_to_drop:
        #             r.pop(key, None)
        #         data.append(r)
        
        # with self.step(f'Load {name}'):
        #     self.default_db.load_data(f"logs_{name}", data, replace=True)

        return self.success()