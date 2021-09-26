import requests
from bs4 import BeautifulSoup
from sayn import PythonTask


class LoadData(PythonTask):

    def run(self):

        url = self.parameters['url_ti10']
        base_url = self.parameters['base_url_liq']

        self.set_run_steps(
            [
                "Get team URLs",
                "Get player roles",
                "Sanitisation",
                "Load roles"
            ]
        )

        with self.step('Get team URLs'):
            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'html.parser')
            teams = soup.find_all('div', class_ = 'teamcard toggle-area toggle-area-1')      
            team_urls = [team.find_next('a').get_attribute_list('href')[0] for team in teams]       

        with self.step('Get player roles'):
            player_info = []

            for team_url in team_urls:   
                page = requests.get(base_url+team_url)
                soup = BeautifulSoup(page.text, 'html.parser')
                roster_table = soup.find('table', class_ = 'wikitable wikitable-striped roster-card')
                player_names = roster_table.find_all('span', {"id": "player"})
                roles = roster_table.find_all('td', {"class": "PositionWoTeam2"})
                if not roles:
                    roles = roster_table.find_all('td', {"class": "Position"})
                player_tags = [player.find('a').get_attribute_list('title')[0] for player in player_names]
                player_roles = [role.text[-1] for role in roles]
                player_dict = dict(zip(player_tags, player_roles))
                player_info.append(player_dict)

        with self.step('Sanitisation'):
            player_list = []
            for team in player_info:
                for key,value in team.items():
                    if value == '5' or value == ')':
                        value = '4'
                    team[key] = int(value)
                    new_dict = {'name': key, 'role': value}
                    player_list.append(new_dict)


        with self.step('Load roles'):
            self.default_db.load_data("logs_roles", player_list, replace=True)

        return self.success()
