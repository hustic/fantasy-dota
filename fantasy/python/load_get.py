import requests

from sayn import PythonTask


class LoadData(PythonTask):

    def run(self):

        base_url = self.parameters['base_url']
        api_key = self.parameters['api_key']

        keys_to_drop = self.parameters['keys_drop']
        api_call = self.parameters['api_call']
        name = self.parameters['name']

        self.set_run_steps(
            [
                "Get from API",
                "Filter",
                "Drop Columns",
                f"Load {name}",
            ]
        )

        with self.step("Get from API"):
            resp = requests.get(
                    f'{base_url}/{api_call}?api_key={api_key}').json()

        with self.step('Drop Columns'):
            data = []
            for r in resp:
                for key in keys_to_drop:
                    r.pop(key, None)
                data.append(r)
        
        with self.step(f'Load {name}'):
            self.default_db.load_data(f"logs_{name}", data, replace=True)

        return self.success()
