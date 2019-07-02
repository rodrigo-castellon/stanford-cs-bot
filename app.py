import os
import json
import subprocess

import retrieve_msgs
import run_stats

from config import *
from command_util import *
from html_util import *

from datetime import datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from flask import Flask, request, render_template

from flask_table import Table, Col

app = Flask(__name__, template_folder='templates')

last_updated = datetime(2019, 1, 1)

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        data = request.get_json()
        text = data['text'].lower()

        global last_updated
        if (datetime.now() - last_updated).seconds > 30:
            retrieve_msgs.main(GROUP_NAME, False)
            last_updated = datetime.now()


        if data['name'] != BOT_NAME:
            if text[0] == '!':
                split_text = text.split()
                command = split_text[0][1:]
                args = split_text[1:]

                if command == 'update':
                    retrieve_msgs.main(GROUP_NAME, False)
                elif command in commands.keys():
                    send_message(get_response(command, args))
    else:
        # do things related to displaying the webpage with stats
        l, total_stats = run_stats.show_stats(run_stats.get_likes)
        table = gen_table(l)

        return render_template('stats.html', table=table)

    return "ok", 200

def send_message(msg):
    url  = 'https://api.groupme.com/v3/bots/post'

    data = {
        'bot_id' : os.getenv('GROUPME_BOT_ID'),
        'text'   : msg,
    }
    request = Request(url, urlencode(data).encode())
    json = urlopen(request).read().decode()
