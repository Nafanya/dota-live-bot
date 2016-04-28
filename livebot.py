import time
import pprint
import telepot

def handle(msg):
    pprint.pprint(msg)

# probably should load it from file or take as argument
TOKEN = 'put it here'

bot = telepot.Bot(TOKEN)
bot.message_loop(handle)
print ('Listening ...')

while True:
    time.sleep(10)
