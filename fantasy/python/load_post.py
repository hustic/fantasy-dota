import requests
import json
import time
from pathos.helpers import cpu_count
from p_tqdm import p_umap

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
        match_ids = [list(d.values())[0] for d in match_ids]

        # print(match_ids[:1])

        def get_job_id(m, base_url, api_key):
            res = {'match_id': m, 'job_id': requests.post(
                f'{base_url}/request/{m}?api_key={api_key}').json()['job']['jobId'],
                'active': True}
            # print(res)
            time.sleep(float(cpu_count())*0.5)
            return res

        jobs = []
        # print(pa.helpers.cpu_count())

        jobs = p_umap(get_job_id, match_ids, [base_url for m in match_ids], [
                            api_key for m in match_ids])
        # jobs = [requests.post(f'{base_url}/request/{m}?api_key={api_key}').json()[
        #                       'job']['jobId'] for m in match_ids[:1]]
        # jobs = [155900072]
        # print(jobs)

        job_ids = [j['job_id'] for j in jobs]

        while job_ids:
            for i, job in enumerate(job_ids):
                resp = requests.get(
                    f'{base_url}/request/{job}?api_key={api_key}')
                if resp.text == 'null':
                    del job_ids[i]
                time.sleep(0.5)

        self.default_db.load_data("logs_jobs", jobs, replace=True)

        return self.success()
