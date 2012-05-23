import web
import time
import hashlib
import cotutil

db = web.database(dbn="postgres", db="cot", user="cot", pw="c0t00t13")
#db = web.database(dbn='sqlite', db='cot.db')

def get_user(id=None, username=None, email=None, password=None):
    wheres = []
    if id:
        wheres.append("(id=$id)")
    if username is not None:
        wheres.append("(username ILIKE $username)")
    if email is not None:
        wheres.append("(email ILIKE $email)")
    if password is not None:
        password = cotutil.hashpw(password)
        wheres.append("(password=$password)")
    users = db.select('"user"', where=" AND ".join(wheres), vars=locals())
    if users:
        return users[0]
    else:
        return None

def new_user(username, email, password):
    db.insert('"user"',
        username=username, email=email, password=cotutil.hashpw(password)
    )

def set_user_password(username, password):
    db.update('"user"', where="username=$username", vars={'username': username}, password=cotutil.hashpw(password))


def get_comments(viewer_id, page_url, item_id):
    wheres = []
    if viewer_id:
        wheres.append("(page_owner_id=$viewer_id OR private=false)")
    if page_url:
        wheres.append("(page_url=$page_url)")
    if item_id:
        wheres.append("(item_id=$item_id)")
    return db.select('comment',
        order='page_url, item_id, id',
        where=" AND ".join(wheres),
        vars=locals()
    )

def get_pages(page_owner_id):
    return db.query('SELECT DISTINCT page_url FROM comment WHERE page_owner_id=$id', vars={'id': page_owner_id})

def new_comment(page_owner_id, page_url, item_id, content):
    db.insert('comment',
        page_owner_id=page_owner_id, page_url=page_url, item_id=item_id, content=content
    )

def del_comment(id):
    db.delete('comment', where="id=$id", vars=locals())
