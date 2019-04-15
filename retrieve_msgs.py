"""
@author: youyanggu (edited by rodrigo-castellon)

Tool to retrieve GroupMe messages using the GroupMe API and output them to a CSV file.

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

########## STAT FUNCTIONS ##########

def get_num_favorited(msg):
    """Counts the number of favorites the mssage received."""
    num_favorited = msg['favorited_by']
    return len(num_favorited)

####################################


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
    Returns a dictionary with group names as keys and a dictionary of
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

def get_group(group_id, direct_msgs=False):
    if direct_msgs:
        params = {'other_user_id' : group_id}
        group = get(requests.get(URL + '/direct_messages' + TOKEN, params=params))
    else:
        group = get(requests.get(URL + '/groups/' + group_id + '?token=' + TOKEN))
    return group

def get_group_count(group_id, direct_msgs):
    group = get_group(group_id, direct_msgs)
    if direct_msgs:
        return int(group['count'])
    else:
        return int(group['messages']['count'])

def get_group_names(groups):
    return groups.keys()

def get_last_msg_id(group_id, direct_msgs):
    group = get_group(group_id, direct_msgs)
    if direct_msgs:
        return group['direct_messages'][0]['id']
    else:
        return group['messages']['last_message_id']

def get_messages(group_id, direct_msgs, before_id=None, since_id=None):
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
        if direct_msgs:
            params['other_user_id'] = group_id
            msgs = get(requests.get(URL + '/direct_messages' + TOKEN, params=params))
        else:
            msgs = get(requests.get(URL + '/groups/' + group_id + '/messages?token=' + TOKEN, params=params))

    except ValueError:
        return []
    return msgs

def countMsgs(group_name, group_id, direct_msgs, csv_file=None, processTextFunc=None, sinceTs=0):
    """
    Call GroupMe API and process messages of a particular group.

    Parameters:
    group_name (bytes): name of group
    group_id (string): id of group
    csv_file (string): name of output csv file
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
                                           user VARCHAR(100),
                                           msg TEXT,
                                           likes INTEGER)""")

    if csv_file:
        f = open(csv_file, "a")
        wr = csv.writer(f, dialect="excel")
        print('creating csv file {}'.format(csv_file))
        print('directory contents: {}'.format(os.listdir()))
    
    if type(sinceTs) == datetime.datetime:
        sinceTs = int(sinceTs.strftime("%s"))
    
    total_count = get_group_count(group_id, direct_msgs)
    print("Counting messages for {} (Total: {})".format(group_name, total_count))
    cur_count = 0
    users = {}
    lastMsgId = str(int(get_last_msg_id(group_id, direct_msgs))+1) # get current msg as well
    while (cur_count < total_count):
        if cur_count % 100 == 0:
            print(cur_count)
        msgs = get_messages(group_id, direct_msgs, lastMsgId)
        if not msgs:
            break
        if direct_msgs:
            msgs = msgs['direct_messages']
        else:
            msgs = msgs['messages']
        if not msgs:
            break
        for msg in msgs:
            if msg['created_at'] < sinceTs:
                return cur_count, users
            cur_count += 1
            try:
                created_at = datetime.datetime.fromtimestamp(msg['created_at']).strftime('%Y-%m-%d %H:%M:%S')
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
            if csv_file:
                wr.writerow([group_name, created_at.encode('utf-8'), user.encode('utf-8'), text.encode('utf-8'), likes])
                cur.execute("INSERT INTO msgcounts (group_name, created_at, user, msg, likes) VALUES (%s, %s, %s, %s, %s)", (group_name,
                                                                                                                             created_at.isoformat(),
                                                                                                                             user,
                                                                                                                             text,
                                                                                                                             likes))
                print('wrote row {}'.format([group_name, created_at.encode('utf-8'), user.encode('utf-8'), text.encode('utf-8'), likes]))
            if processTextFunc is not None:
                data = processTextFunc(msg)
                users[user].append(data)
        lastMsgId = msgs[-1]['id']
    if csv_file:
        f.close()
    
    # commit and close connection to database
    conn.commit()
    curr.close()
    conn.close()
    return cur_count, users

def main(group_name, csv_file, overwrite):
    if type(group_name) == type(''):
        group_name = group_name.encode('utf-8').strip()
    groups = get_groups()
    if groups is None:
        raise RuntimeError("Cannot retrieve groups. Is your token correct?")

    if group_name not in groups:
        print("Group name not found. Here are the list of groups:")
        print(get_group_names(groups))
    else:
        if csv_file and os.path.isfile(csv_file) and not overwrite:
            raise IOError("File already exists. Try setting --overwrite.")
        if not csv_file:
            csv_file = group_name.decode('utf-8').lower().replace(' ', '_')+'.csv'
        count, _ = countMsgs(group_name, groups[group_name]['id'], False, csv_file=csv_file)
        print("Processed {} messages. Wrote to {}.".format(count, csv_file))
        print('directory contents: {}'.format(os.listdir()))


