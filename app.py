import os
import json

from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    text = data['text'].lower()

    # We don't want to reply to ourselves!
    if data['name'] != 'Botty McBotFace':
        if any(x in text for x in ['group chat', ' gc']):
            msg = 'Speaking of group chats, check out the group chat list: https://bit.ly/2FuzbPs'
            send_message(msg)

    return "ok", 200

def send_message(msg):
    url  = 'https://api.groupme.com/v3/bots/post'

    data = {
        'bot_id' : os.getenv('GROUPME_BOT_ID'),
        'text'   : msg,
    }
    request = Request(url, urlencode(data).encode())
    json = urlopen(request).read().decode()
