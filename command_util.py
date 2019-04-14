import random
import run_stats
from config import GROUP_NAME

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

def eight_ball(args):
    global eightball
    if len(args) == 0:
        return 'You need a question for me to answer!'
    else:
        return random.choice(eightball)

def stats(args):
    fname = GROUP_NAME.decode('utf-8').lower().replace(' ', '_')+'.csv'
    return run_stats.show_stats(fname)

commands = {
    'help': 'Here are some of my commands: !help, !social, !gc, !8ball, and !stats',
    'gc': 'Find other admitted Stanford group chats on this list: https://bit.ly/2FuzbPs',
    'social': 'Find other admitted trees\' social medias on this spreadsheet: https://bit.ly/2FMwDxm',
    '8ball': eight_ball,
    'stats': stats
}

def get_response(cmd, args):
    global commands
    if type(commands[cmd]) == type(''):
        return commands[cmd]
    elif type(commands[cmd]) == type(lambda x: x):
        return commands[cmd](args)