import web
import time

db = web.database(dbn="postgres", db="cot", user="cot", pw="c0t00t13")
#db = web.database(dbn='sqlite', db='cot.db')

def get_user(name):
    users = db.select('account', where='username ILIKE $name', vars=locals())
    if users:
        return users[0]
    else:
        return None

def get_comments():
    return db.select('comment', order='page_url, item_id, id')

def new_comment(page_owner_id, page_url, item_id, content):
    db.insert('comment',
        page_owner_id=page_owner_id, page_url=page_url, item_id=item_id, content=content
    )

def del_comment(id):
    db.delete('comment', where="id=$id", vars=locals())
