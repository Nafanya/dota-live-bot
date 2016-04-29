import time
import telepot

from steamapi import get_live_games_stats


def handle(msg):
    print msg['text'] + ' from ' + str(msg['chat']['id'])
    if msg['text'] == '/live':
        sender = int(msg['chat']['id'])
        for game in get_live_games_stats():
            bot.sendMessage(sender, game)


def load_token():
    with open('tokens/telegram', 'r') as token_file:
        return token_file.read().replace('\n', '')


bot = telepot.Bot(load_token())
bot.message_loop(handle)
print ('Listening ...')

while True:
    time.sleep(10)
