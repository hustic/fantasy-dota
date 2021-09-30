import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
import time

from pathos.helpers import cpu_count
from p_tqdm import p_umap
from tqdm import tqdm

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

        self.set_run_steps(
            [
                "Get match_ids from DB",
                "Submit jobs",
                "Check for jobs done",
                "Load Jobs",
            ]
        )

        with self.step("Get match_ids from DB"):
            match_ids = self.default_db.read_data(self.query)
            match_ids = [list(d.values())[0] for d in match_ids]

        def get_job_id(m, base_url, api_key):
            retry_strategy = Retry(
                total=10,
                status_forcelist=(429, 500, 502, 503, 504),
                backoff_factor=2
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            http = requests.Session()
            http.mount("https://", adapter)
            http.mount("http://", adapter)
            request = http.post(
                f'{base_url}/request/{m}?api_key={api_key}')

            try:
                job_id = request.json()['job']['jobId']
                res = {'match_id': m, 'job_id': job_id, 'active': True}
            except:
                print(request)

            time.sleep(float(cpu_count())*0.05)
            return res

        with self.step("Submit jobs"):
            jobs = []

            jobs = p_umap(get_job_id, match_ids, [base_url for m in match_ids], [
                                api_key for m in match_ids])

            job_ids = [j['job_id'] for j in jobs]

        with self.step("Check for jobs done"):
            pbar = tqdm(total=len(job_ids))
            while job_ids:
                for i, job in enumerate(job_ids):
                    resp = requests.get(
                        f'{base_url}/request/{job}?api_key={api_key}')
                    if resp.text == 'null':
                        del job_ids[i]
                        pbar.update(1)
                    time.sleep(0.05)
            pbar.close()

        with self.step("Load Jobs"):
            self.default_db.load_data("logs_jobs", jobs, replace=True)

        return self.success()
