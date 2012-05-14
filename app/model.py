import web
import time

db = web.database(dbn="postgres", db="cot", user="cot", pw="c0t00t13")
#db = web.database(dbn='sqlite', db='cot.db')

def get_comments():
    return db.select('comment', order='page_url, item_id, id')

def new_comment(page_owner_id, page_url, item_id, content):
    db.insert('comment',
        page_owner_id=page_owner_id, page_url=page_url, item_id=item_id, content=content,
        date_posted = time.time()
    )

def del_comment(id):
    db.delete('comment', where="id=$id", vars=locals())
