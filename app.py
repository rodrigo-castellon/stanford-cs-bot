import random
import os
import json

import retrieve_msgs
from config import *
from datetime import datetime

from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Flask, request

app = Flask(__name__)

eightball = [
    'It is certain.',
    'It is decidedly so.',
    'Without a doubt.',
    'Yes - definitely.',
    'You may rely on it.',
    'As I see it, yes.',
    'Most likely.',
    'Outlook good.',
    'Yes.',
    'Signs point to yes.',
    'Reply hazy, try again.',
    'Ask again later.',
    'Better not tell you now.',
    'Cannot predict now.',
    'Concentrate and ask again.',
    'Don\'t count on it.',
    'My reply is no.',
    'My sources say no.',
    'Outlook not so good.',
    'Very doubtful.'
]
def eight_ball(text=None):
    global eightball
    return random.choice([eightball])

commands = {
    'help': 'Here are some of my commands: !help, !social, !gc',
    'gc': 'Find other admitted Stanford group chats on this list: https://bit.ly/2FuzbPs',
    'social': 'Find other admitted trees\' social medias on this spreadsheet: https://bit.ly/2FMwDxm'
    '8ball': eight_ball
}
def get_response(cmd):
    global commands
    if type(commands[cmd]) == type(''):
        return commands[cmd]
    elif type(commands[cmd]) == type(lambda x: x):
        return commands[cmd]()

last_updated = datetime(2019, 1, 1)

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    text = data['text'].lower()

    global last_updated
    if (datetime.now() - last_updated).seconds > 3600:
        last_updated = datetime.now()
        #retrieve_msgs.main(False, False, )


    if data['name'] != BOT_NAME:
        if text[0] == '!':
            command = text[1:]
            if command in commands.keys():
                send_message(get_response(command))
            else:
                send_message('Sorry, I don\'t know what that command is. Try again?')

    return "ok", 200

def send_message(msg):
    url  = 'https://api.groupme.com/v3/bots/post'

    data = {
        'bot_id' : os.getenv('GROUPME_BOT_ID'),
        'text'   : msg,
    }
    request = Request(url, urlencode(data).encode())
    json = urlopen(request).read().decode()
