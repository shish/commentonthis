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

    users = db.select('"user"',
        where=" AND ".join(wheres),
        vars=locals()
    )
    if users:
        return users[0]
    else:
        return None

def new_user(username, email, password):
    db.insert('"user"',
        username=username,
        email=email,
        password=cotutil.hashpw(password)
    )

def set_user_password(username, password):
    db.update('"user"',
        where="username=$username",
        vars={'username': username},
        password=cotutil.hashpw(password)
    )

def set_user_mailmode(username, mode):
    db.update('"user"',
        where="username=$username",
        vars={'username': username},
        mailmode=mode
    )


def get_comment(id=None):
    comments = db.select('"comment"',
        where="id=$id",
        vars=locals()
    )
    if comments:
        return comments[0]
    else:
        return None

def get_comments(viewer_id, page_url=None, item_id=None, page_owner_id=None, commenter_id=None, limit=None):
    wheres = []
    if viewer_id:
        wheres.append("(page_owner_id=$viewer_id OR private=false)")
    if page_url:
        wheres.append("(page_url=$page_url)")
    if item_id:
        wheres.append("(item_id=$item_id)")
    if page_owner_id:
        wheres.append("(page_owner_id=$page_owner_id)")
    if commenter_id:
        wheres.append("(commenter_id=$commenter_id)")

    if limit:
        limit = "LIMIT %d" % limit
    else:
        limit = ""

    return db.query(
        "SELECT *, page_owner.username AS page_owner, commenter.username AS commenter "+
        "FROM comment "+
        "JOIN \"user\" AS page_owner ON comment.page_owner_id = page_owner.id "+
        "JOIN \"user\" AS commenter ON comment.commenter_id = commenter.id "+
        "WHERE "+" AND ".join(wheres)+" "+
        "ORDER BY page_url, item_id, comment.id "+
        limit,
        vars=locals()
    )

def get_pages(page_owner_id, limit=None):
    return db.select('comment',
        what="page_url, COUNT(id) AS comments",
        where='page_owner_id=$id',
        group='page_url',
        limit=limit,
        vars={'id': page_owner_id}
    )

def new_comment(page_owner_id, page_url, item_id, content, commenter_id):
    db.insert('comment',
        page_owner_id=page_owner_id,
        page_url=page_url,
        item_id=item_id,
        content=content,
        commenter_id=commenter_id
    )

def del_comment(id):
    db.delete('comment',
        where="id=$id",
        vars=locals()
    )


def get_messages(user_id, limit=None):
    if limit:
        limit = "LIMIT %d" % limit
    else:
        limit = ""

    return db.query(
        "SELECT *, user_from.username AS user_from "+
        "FROM message "+
        "JOIN \"user\" AS user_from ON message.user_id_from = user_from.id "+
        "WHERE user_id_to=$user_id "+
        limit,
        vars={'user_id': user_id}
    )

def new_message(from_id, to_id, content):
    db.insert('message',
        user_id_from = from_id,
        user_id_to = to_id,
        content = content
    )
