import dota2api


def load_token():
    with open('tokens/steam', 'r') as token_file:
        return token_file.read().replace('\n', '')


def get_important_leagues():
    leagues = dict()
    for league in [x.split(' ', 1) for x in list(open('leagues.txt', 'r'))]:
        leagues[int(league[0])] = league[1]
    return leagues


def get_time(time):
    minutes = int(time) / 60
    seconds = int(time) % 60
    return str(minutes) + ':' + str(seconds)


def get_game_info(game_id):
    # no idea what im doing
    try:
        game_id['scoreboard']
    except KeyError:
        return '> Whoops.'
    nw = {'dire': 0, 'radiant': 0}
    for player in game_id['scoreboard']['dire']['players']:
        nw['dire'] += player['net_worth']
    for player in game_id['scoreboard']['radiant']['players']:
        nw['radiant'] += player['net_worth']
    message = game_id['radiant_team']['team_name'] + ' vs. ' + game_id['dire_team']['team_name']
    message += ' (' + str(game_id['radiant_series_wins']) + ' - ' + str(game_id['dire_series_wins']) + '), '
    diff = nw['radiant'] - nw['dire']
    if diff < 0:
        message += 'Dire leads by ' + str(-diff) + ' gold'
    else:
        message += 'Radiant leads by ' + str(diff) + ' gold'
    message += ' @ ' + get_time(game_id['scoreboard']['duration'])
    return message


def get_live_games_stats():
    api = dota2api.Initialise(load_token())
    live_games = api.get_live_league_games()
    stats = []
    for game in live_games['games']:
        if game['league_id'] in get_important_leagues():
            stats.append(get_game_info(game))
    if len(stats) == 0:
        return 'Sorry, no live games found.'
    return stats
