""" 
@author: youyanggu (edited by rodrigo-castellon)

Tool to show simple stats of GroupMe messages. It takes the csv file generated 
by retrieve_msgs.py as input.

"""

import os
import psycopg2

### Message processor functions:

def get_occurrences(phrase, count_dups=False, print_matches=False, match_exactly=False, print_user=None):
    """
    Given a phrase, return a function that is passed to read_db to count the number
    of occurrences of a certain phrase.

    Parameters:
    phrase: a single string or a list of strings to match for
    count_dups (boolean): count multiple instances of a phrase in a message as a single instance
    print_matches (boolean): print the messages that match the phrase
    match_exactly (boolean): the message must match the phrase exactly
    print_user (string): when print_matches is true, only print the matches by this user

    """
    def get_num(user, msg, likes):
        count = 0
        if msg is None:
            return 0
        else:
            text = msg.lower()
            if type(phrase) == list:
                for w in phrase:
                    if match_exactly:
                        if text == w:
                            count = 1
                    else:
                        count += text.count(w)
            else:
                if match_exactly:
                    if phrase == text:
                        count = 1
                else:
                    count = text.count(phrase)
            if count > 0 and (print_matches or print_user == user):
                print(user, ':', msg)
            if count_dups:
                return min(count, 1)
            else:
                return count
    return get_num

def get_likes(user, msg, likes)
    return likes

def num_words(user, msg, likes):
    return len(msg.split())

def num_chars(user, msg, likes):
    return len(msg)

##############################

def read_db(process_msg_func=None):
    """
    Read the table `msgcounts` from the database and passes the content to process_msg_func.
    """
    if process_msg_func == None:
        process_msg_func = lambda x,y: 1

    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    cur.execute("SELECT * FROM msgcounts;")
    table = cur.fetchall()

    count = 0
    d = {}
    for row in table:
        ID, group_name, created_at, user, msg, likes = row
        if user not in d:
            d[user] = []
        
        data = process_msg_func(user, msg, likes)
        d[user].append(data)
    return d

def show_stats(func=None, **kwargs):
    """Call `read_db` and `get_stats`"""
    result = read_db(func)
    return get_stats(result, **kwargs)

def get_stats(data, include_groupme=False, total=True, percent=True, compact=True):
    """ 
    Given the return value of read_db, display useful stats.

    Parameters:
    data (dict): key is the user's name and the value is a list that contains an
                 integer for each message by the user (typically representing the # of phrases matched)
    include_groupme (boolean): include messages sent by GroupMe
    total (boolean): If this isn't true, then we take the average of integer data. If we're counting phrase 
                     occurrences, then total=True. If we are counting avg message length, then total=False
    percent (boolean): display the number of matches as a percentage of total messages
    compact (boolean): don't return the total num of messages and percentage

    Returns:
    A list `l` where each element contains statistics for each person and
    a list `total_stats` which contains total messages and total data
    """
    l = []
    total_stats = [-1, 0, 0]
    num_people = len(data.keys())
    total_msgs = total_data_per_person = total_data = 0
    for user, ints in data.items():
        if not include_groupme and user == 'GroupMe':
            continue
        # stats: username, # of messages, total data, data per msg
        user_stats = (user, len(ints), sum(ints), sum(ints)/len(ints))
        total_stats[1:] = [user_stats[i+1] + x for i,x in enumerate(total_stats[1:])]
        l.append(user_stats)

    l = sorted(l, key=lambda k:k[1], reverse=True)

    return l, total_stats















