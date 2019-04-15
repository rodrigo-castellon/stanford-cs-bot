import os
import json
import subprocess

import retrieve_msgs
import run_stats

from config import *
from command_util import *

from datetime import datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from flask import Flask, request, render_template

app = Flask(__name__, template_folder='template')

last_updated = datetime(2019, 1, 1)

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        data = request.get_json()
        text = data['text'].lower()

        global last_updated
        if (datetime.now() - last_updated).seconds > 3600:
            pass#last_updated = datetime.now()


        if data['name'] != BOT_NAME:
            send_message(str((datetime.now() - last_updated).seconds))
            if text[0] == '!':
                split_text = text.split()
                command = split_text[0][1:]
                args = split_text[1:]

                if command == 'update':
                    retrieve_msgs.main(GROUP_NAME, False)
                elif command in commands.keys():
                    send_message(get_response(command, args))
                else:
                    proc = subprocess.Popen([command, *args], stdout=subprocess.PIPE)
                    output, error = proc.communicate()
                    send_message('||LINUX OUTPUT|| {}'.format(output))
                    send_message('||LINUX ERRORS|| {}'.format(error))
    else:
        # do things related to displaying the webpage with stats
        return render_template('stats.html')

    return "ok", 200

def send_message(msg):
    url  = 'https://api.groupme.com/v3/bots/post'

    data = {
        'bot_id' : os.getenv('GROUPME_BOT_ID'),
        'text'   : msg,
    }
    request = Request(url, urlencode(data).encode())
    json = urlopen(request).read().decode()
