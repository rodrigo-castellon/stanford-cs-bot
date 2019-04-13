import os
import json

import retrieve_msgs
from config import *
from command_util import *

from datetime import datetime

from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Flask, request

app = Flask(__name__)

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
            text = text.split()
            command = text[0][1:]
            args = text[1:]
            if command in commands.keys():
                send_message(get_response(command, args))
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
