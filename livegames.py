import json
import subprocess

import dota2api
import os
import requests

from config.tokens.tokens import STEAM_TOKEN


with open('templates/base.html') as f:
    TEMPLATE = f.read()


def get_important_leagues():
    leagues = dict()
    for league in [x.split(' ', 1) for x in list(open('config/top_leagues.txt', 'r'))]:
        leagues[int(league[0])] = league[1]
    return leagues


def get_abbreviations():
    teams = dict()
    for team in [x.split(' ', 1) for x in list(open('config/teams.txt', 'r'))]:
        teams[int(team[0])] = team[1].replace('\n', '')
    return teams


def get_time(game_id):
    minutes = int(game_id['scoreboard']['duration']) // 60
    seconds = int(game_id['scoreboard']['duration']) % 60
    return str(minutes).zfill(2) + ':' + str(seconds).zfill(2)


def get_team_name(game_id, side):
    try:
        team_id = game_id[side + '_team']['team_id']
        abbreviations = get_abbreviations()
        if team_id in abbreviations:
            return abbreviations[team_id]
        else:
            return game_id[side + '_team']['team_name']
    except KeyError:
        return 'Unknown team'


def get_teams(game_id):
    return get_team_name(game_id, 'radiant') + ' vs. ' + get_team_name(game_id, 'dire')


def get_networth(game_id):
    nw_radiant = sum(player['net_worth'] for player in game_id['scoreboard']['radiant']['players'])
    nw_dire = sum(player['net_worth'] for player in game_id['scoreboard']['dire']['players'])
    return nw_radiant, nw_dire


def get_xp(game_id):
    seconds = game_id['scoreboard']['duration']
    xp_radiant = int(sum(player['xp_per_min'] for player in game_id['scoreboard']['radiant']['players']) * seconds / 60)
    xp_dire = int(sum(player['xp_per_min'] for player in game_id['scoreboard']['dire']['players']) * seconds / 60)
    return xp_radiant, xp_dire


def get_leads(game_id):
    nw_radiant, nw_dire = get_networth(game_id)
    xp_radiant, xp_dire = get_xp(game_id)
    nw_diff = str(abs(nw_radiant - nw_dire))
    xp_diff = str(abs(xp_radiant - xp_dire))
    if nw_radiant > nw_dire:
        if xp_radiant > xp_dire:
            text = 'radiant leads by ' + nw_diff + ' gold and ' + xp_diff + ' XP'
        else:
            text = 'radiant leads by ' + nw_diff + ' gold, dire leads by ' + xp_diff + ' XP'
    else:
        if nw_dire > nw_radiant:
            text = 'dire leads by ' + nw_diff + ' gold and ' + xp_diff + ' XP'
        else:
            text = 'dire leads by ' + nw_diff + ' gold, radiant leads by ' + xp_diff + ' XP'
    return text + ' @ ' + get_time(game_id)


def get_kills(game_id):
    kills_radiant = sum(player['kills'] for player in game_id['scoreboard']['radiant']['players'])
    kills_dire = sum(player['kills'] for player in game_id['scoreboard']['dire']['players'])
    return str(kills_radiant) + ' - ' + str(kills_dire)


def get_series_score(game_id):
    return str(game_id['radiant_series_wins']) + ' - ' + str(game_id['dire_series_wins'])


def get_game_info(game_id):
    # no idea what im doing
    try:
        game_id['scoreboard']
    except KeyError:
        return '> Whoops.'

    message = get_teams(game_id)
    if int(game_id['scoreboard']['duration']) == 0:
        return message + ', drafting'
    message += ', '
    message += get_kills(game_id)
    message += ', '
    message += get_leads(game_id)
    return message


def get_live_games_stats():
    api = dota2api.Initialise(STEAM_TOKEN)
    live_games = api.get_live_league_games()
    stats = []
    for game in live_games['games']:
        if game['league_id'] in get_important_leagues() or game['spectators'] > 1000:
            stats.append(get_game_info(game))
    if len(stats) == 0:
        stats.append('Sorry, no live games found.')
    return stats


def get_team_image_url(game_id, side):
    img_url = 'http://api.steampowered.com/ISteamRemoteStorage/GetUGCFileDetails/v1/?key={key}&appid=570&ugcid={team_logo}'
    try:
        team_logo = game_id[side + '_team']['team_logo']
    except KeyError:
        return 'No image'
    response = requests.get(img_url.format(key=STEAM_TOKEN, team_logo=team_logo))
    print(response.text)
    jsn = json.loads(response.text)
    try:
        return jsn['data']['url']
    except KeyError:
        return 'No image'


def get_team_images(game_id):
    radiant = get_team_image_url(game_id, 'radiant')
    dire = get_team_image_url(game_id, 'dire')
    return {
        'radiant': radiant,
        'dire': dire
    }


# Same as get_leads but without time
def get_leads2(game_id):
    nw_radiant, nw_dire = get_networth(game_id)
    xp_radiant, xp_dire = get_xp(game_id)
    nw_diff = str(abs(nw_radiant - nw_dire))
    xp_diff = str(abs(xp_radiant - xp_dire))
    if nw_radiant > nw_dire:
        if xp_radiant > xp_dire:
            text = 'radiant leads by ' + nw_diff + ' gold and ' + xp_diff + ' XP'
        else:
            text = 'radiant leads by ' + nw_diff + ' gold, dire leads by ' + xp_diff + ' XP'
    else:
        if nw_dire > nw_radiant:
            text = 'dire leads by ' + nw_diff + ' gold and ' + xp_diff + ' XP'
        else:
            text = 'dire leads by ' + nw_diff + ' gold, radiant leads by ' + xp_diff + ' XP'
    return text


def render_game(game_id):
    try:
        game_id['scoreboard']
    except KeyError:
        return '> Whoops.'

    match_id = game_id['match_id']
    radiant = get_team_name(game_id, 'radiant')
    dire = get_team_name(game_id, 'dire')
    duration = int(game_id['scoreboard']['duration'])
    if duration == 0:
        game_time = 'drafting'
    else:
        game_time = get_time(game_id)
    images = get_team_images(game_id)
    output_path = 'templates/responses/{}.png'.format(match_id)
    output_html = 'templates/responses/{}.html'.format(match_id)
    with open(output_html, 'w') as out:
        out.write(TEMPLATE
                  .replace('RADIANT_NAME', radiant)
                  .replace('DIRE_NAME', dire)
                  .replace('GAME_TIME', game_time)
                  .replace('GAME_KILLS', get_kills(game_id))
                  .replace('GAME_LEADS', get_leads2(game_id))
                  .replace('RADIANT_IMG', images['radiant'])
                  .replace('DIRE_IMG', images['dire']))
    subprocess.call(['python2', 'python-webkit2png/webkit2png/scripts.py', '-o', output_path, '-g', '550', '150', output_html])
    return output_path


def get_img_live_game_stats():
    api = dota2api.Initialise(STEAM_TOKEN)
    live_games = api.get_live_league_games()
    important_leagues = get_important_leagues()
    stats = list()
    for game in live_games['games']:
        if game['league_id'] in important_leagues or game['spectators'] > 100:
            stats.append(render_game(game))
    return stats


if __name__ == '__main__':
    print(get_img_live_game_stats())