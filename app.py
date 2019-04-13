import os
import json

from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Flask, request

app = Flask(__name__)

commands = {
    'help': 'commands: !help, !social, !gc',
    'gc': 'Find other admitted Stanford group chats on this list: https://bit.ly/2FuzbPs',
    'social': 'Find other admitted trees\' social medias on this spreadsheet: '
}

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    text = data['text'].lower()

    # We don't want to reply to ourselves!
    if data['name'] != 'Botty McBotFace' and text[0] == '!':
        command = text[1:]
        if command in commands.keys():
            send_message(commands[command])
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
