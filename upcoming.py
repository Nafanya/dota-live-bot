import requests
import time
from datetime import datetime, timedelta
from dateutil import parser

from bs4 import BeautifulSoup
import dota2api


def load_token():
    with open('config/tokens/steam', 'r') as token_file:
        return token_file.read().replace('\n', '')


def load_leagues():
    api = dota2api.Initialise(load_token())
    with open('config/leagues.txt', 'w') as outfile:
        for league in api.get_league_listing()['leagues']:
            outfile.write(str(league['leagueid']) + ' ' + league['name'].encode('UTF-8') + '\n')


def get_upcoming(wiki_url):
    upcoming_games = []
    r = requests.get(wiki_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for game in soup.find_all('div', {'class': 'bracket-game'}):
        game_time = game.find('span', {'class': 'datetime'})
        if game_time is None:
            continue
        game_time = game_time.get_text()
        teams = [x.find('div').find('span').find('span', {'class': 'team-template-text'}).get_text() for x in
                 game.find_all('div', {'class': 'bracket-cell-r2'})]
        if len(teams) < 2:
            missing = 2 - len(teams)
            for i in range(missing):
                teams.append('TBD')
        message = teams[0] + ' vs. ' + teams[1] + ' ' + time_to_go(game_time)
        upcoming_games.append(message)
    return upcoming_games


def time_to_go(game_date):
    tzinfos = {'CEST': 2}
    game_tz = tzinfos[game_date.split(' ')[-1]]
    current_tz = time.timezone / -3600
    start_time = parser.parse(game_date[:game_date.rfind(' ')]) + timedelta(hours=current_tz - game_tz)
    if start_time < datetime.now():
        return 'LIVE'
    to_go = start_time - datetime.now()
    hours = int(timedelta.total_seconds(to_go) / 3600)
    minutes = int(timedelta.total_seconds(to_go) % 3600) / 60
    return 'in ' + str(hours).zfill(2) + ':' + str(minutes).zfill(2)
