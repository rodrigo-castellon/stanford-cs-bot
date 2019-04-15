from flask_table import Table, Col

# Declare your table
class ItemTable(Table):
    name = Col('Name')
    msgs = Col('Messages')
    total_likes = Col('Total Likes')
    likes_per = Col('Likes per Message')

# Get some objects
class Item(object):
    def __init__(self, name, msgs, total_likes, likes_per):
        self.name = name
        self.msgs = msgs
        self.total_likes = total_likes
        self.likes_per = likes_per

def gen_table(l):
	items = [list(x) for x in l]
	table = ItemTable(items)
	return table