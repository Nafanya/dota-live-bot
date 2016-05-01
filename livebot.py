import time
import telepot
import logging
import datetime

from livegames import get_live_games_stats
from upcoming import get_upcoming


def handle(msg):
    logger.info(msg['text'] + ' from ' + str(msg['chat']['id']) + ' @ ' + str(datetime.datetime.now()))
    if msg['text'] == '/live':
        for game in get_live_games_stats():
            bot.sendMessage(int(msg['chat']['id']), game)
    elif msg['text'] == '/upcoming':
        url = 'http://wiki.teamliquid.net/dota2/WePlay_Dota2_League/Season_3'
        for game in get_upcoming(url):
            bot.sendMessage(int(msg['chat']['id']), game)



def load_token():
    with open('config/tokens/telegram', 'r') as token_file:
        return token_file.read().replace('\n', '')


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.FileHandler('bot.log')
handler.setLevel(logging.INFO)
logger.addHandler(handler)

bot = telepot.Bot(load_token())
bot.message_loop(handle)
print ('Listening ...')

while True:
    time.sleep(10)
