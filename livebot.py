import datetime
import logging
import time

import telepot
from config.tokens.tokens import TELEGRAM_TOKEN
from livegames import get_img_live_game_stats, get_live_games_stats
from upcoming import get_upcoming


def handle(msg):
    logger.info(msg['text'] + ' from ' + str(msg['chat']['id']) + ' @ ' + str(datetime.datetime.now()))
    text = msg['text']
    if text == '/start':
        bot.sendMessage(int(msg['chat']['id']), 'Hi! Send /live to see live matches, /liveimg to see them as images and /upcoming for upcoming games')
    elif text == '/live':
        for game in get_live_games_stats():
            bot.sendMessage(int(msg['chat']['id']), game)
    elif text == '/liveimg':
        for game_img in get_img_live_game_stats():
            with open(game_img, 'rb') as photo:
                bot.sendPhoto(int(msg['chat']['id']), photo)
    elif text == '/upcoming':
        url = 'http://wiki.teamliquid.net/dota2/WePlay_Dota2_League/Season_3'
        for game in get_upcoming(url):
            bot.sendMessage(int(msg['chat']['id']), game)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    handler = logging.FileHandler('bot.log')
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)

    bot = telepot.Bot(TELEGRAM_TOKEN)
    bot.message_loop(handle)
    print ('Listening ...')

    while True:
        time.sleep(10)
