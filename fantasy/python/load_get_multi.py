import requests
import time

from sayn import PythonTask


class LoadData(PythonTask):

    def run(self):

        base_url = self.parameters['base_url']
        api_key = self.parameters['api_key']

        keys_to_drop = self.parameters['keys_drop']
        api_call = self.parameters['api_call']
        name = self.parameters['name']

        minimum_number_of_matches = self.parameters['len']

        self.set_run_steps(
            [
                "Get from API",
                "Filter",
                "Drop Columns",
                f"Load {name}",
            ]
        )

        with self.step("Get from API"):
            matches = []
            first_response = requests.get(
                    f'{base_url}/{api_call}?api_key={api_key}').json()

            matches += first_response
            tmp_ids = [r['match_id'] for r in first_response]

            min_id = min(tmp_ids)

            while len(matches) <= minimum_number_of_matches:
                resp = requests.get(
                    f'{base_url}/{api_call}?api_key={api_key}&less_than_match_id={min_id}').json()
                matches += resp
                tmp_ids = [r['match_id'] for r in resp]
                min_id = min(tmp_ids)
                time.sleep(0.4)

        with self.step('Drop Columns'):
            data = []
            for r in matches:
                for key in keys_to_drop:
                    r.pop(key, None)
                data.append(r)

        with self.step(f'Load {name}'):
            self.default_db.load_data(f"logs_{name}", data, replace=True)

        return self.success()
