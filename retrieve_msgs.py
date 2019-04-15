"""
@author: youyanggu (edited by rodrigo-castellon)

Tool to retrieve GroupMe messages using the GroupMe API and output them to a PostgreSQL database

"""

import json
import requests
import datetime
import csv
import os
import psycopg2

# GroupMe API variables
URL = 'https://api.groupme.com/v3'
TOKEN = os.getenv('GROUPME_BOT_TOKEN')

def get_num_favorited(msg):
    """Counts the number of favorites the mssage received."""
    num_favorited = msg['favorited_by']
    return len(num_favorited)


##########################
#
# GROUPME API Helper Functions
#
##########################

def get(response):
    """Retrieve the 'response' portion of the json object."""
    return response.json()['response']

def get_groups():
    """
    Return a dictionary with group names as keys and a dictionary of
    group id and # of messages as values

    """
    params = {'per_page' : 100}
    groups = get(requests.get(URL + '/groups?token=' + TOKEN, params=params))
    if groups is None:
        return None
    d = {}
    for group in groups:
        name = group['name'].encode('utf-8').strip()
        count = group['messages']['count']
        if count > 0:
            d[name] = {}
            d[name]['id'] = group['group_id']
            d[name]['count'] = count
    return d

def get_group(group_id):
    group = get(requests.get(URL + '/groups/' + group_id + '?token=' + TOKEN))
    return group

def get_group_count(group_id):
    group = get_group(group_id)
    return int(group['messages']['count'])

def get_group_names(groups):
    return groups.keys()

def get_last_msg_id(group_id):
    group = get_group(group_id)
    return group['messages']['last_message_id']

def get_messages(group_id, before_id=None, since_id=None):
    """
    Given the group_id and the message_id, retrieve 20 messages.

    Parameters:
    before_id: take the 20 messages before this message_id
    since_id: take the 20 messages after this message_id (maybe)
    """
    params = {}
    if before_id is not None:
        params['before_id'] = str(before_id)
    if since_id is not None:
        params['since_id'] = str(since_id)
    try:
        print('getting response from complete URL {}'.format(URL + '/groups/' + group_id + '/messages?token=' + TOKEN))
        msgs = get(requests.get(URL + '/groups/' + group_id + '/messages?token=' + TOKEN))#, params=params))

    except ValueError:
        return []
    return msgs

def count_msgs(group_name, group_id, processTextFunc=None, sinceTs=0):
    """
    Call GroupMe API and process messages of a particular group.

    Parameters:
    group_name (bytes): name of group
    group_id (string): id of group
    processTextFunc (function): a function that processes a msg and returns a value that is appended to user data
    sinceTs (int): only process messages after this timestamp
    """

    # Postgres setup
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS msgcounts;")

    cur.execute("""CREATE TABLE msgcounts (id SERIAL PRIMARY KEY,
                                           group_name VARCHAR(100),
                                           created_at TIMESTAMP WITH TIME ZONE,
                                           username VARCHAR(100),
                                           msg TEXT,
                                           likes INTEGER)""")
    
    if type(sinceTs) == datetime.datetime:
        sinceTs = int(sinceTs.strftime("%s"))
    
    total_count = get_group_count(group_id)
    print("Counting messages for {} (Total: {})".format(group_name, total_count))
    cur_count = 0
    users = {}
    lastMsgId = str(int(get_last_msg_id(group_id))+1) # get current msg as well
    while (cur_count < total_count):
        if cur_count % 100 == 0:
            print(cur_count)
        msgs = get_messages(group_id, None, lastMsgId)
        if not msgs:
            break
        else:
            msgs = msgs['messages']
        if not msgs:
            break
        for msg in msgs:
            if msg['created_at'] < sinceTs:
                return cur_count, users
            cur_count += 1
            try:
                created_at = datetime.datetime.fromtimestamp(msg['created_at']).isoformat()
            except:
                print("Error parsing created_at")
                created_at = ""
            user = msg['name']
            text = msg['text']
            likes = get_num_favorited(msg)
            if text is None:
                text = ""
            if user is None:
                user = ""
            if created_at is None:
                created_at = ""
            if user not in users:
                users[user] = []
            cur.execute("INSERT INTO msgcounts (group_name, created_at, username, msg, likes) VALUES (%s, %s, %s, %s, %s)", (group_name.decode(),
                                                                                                                             created_at,
                                                                                                                             user,
                                                                                                                             text,
                                                                                                                             likes))
            print('wrote row {}'.format([group_name, created_at.encode('utf-8'), user.encode('utf-8'), text.encode('utf-8'), likes]))
            if processTextFunc is not None:
                data = processTextFunc(msg)
                users[user].append(data)
        lastMsgId = msgs[-1]['id']
    
    # commit and close connection to database
    conn.commit()
    cur.close()
    conn.close()
    return cur_count, users

def main(group_name, overwrite):
    if type(group_name) == type(''):
        group_name = group_name.encode('utf-8').strip()
    groups = get_groups()
    if groups is None:
        raise RuntimeError("Cannot retrieve groups. Is your token correct?")

    if group_name not in groups:
        print("Group name not found. Here are the list of groups:")
        print(get_group_names(groups))
    else:
        count, _ = count_msgs(group_name, groups[group_name]['id'])
        print("Processed {} messages. Wrote to database.".format(count))


