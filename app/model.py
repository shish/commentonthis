import web
import time
import hashlib
import cotutil
import ConfigParser

config = ConfigParser.SafeConfigParser()
config.read("../app/cot.cfg")

db = web.database(
    dbn  = config.get("database", "dbn"),
    db   = config.get("database", "db"),
    user = config.get("database", "user"),
    pw   = config.get("database", "pw")
)


# ============================================================================
# users

def get_user(name=None, email=None, password=None):
    wheres = []
    if name is not None:
        wheres.append("(lower(name) = lower($name))")
    if email is not None:
        wheres.append("(lower(email) = lower($email))")
    if password is not None:
        password = cotutil.hashpw(password)
        wheres.append("(password=$password)")

    users = db.select('cot_user',
        where=" AND ".join(wheres),
        vars=locals()
    )

    if users:
        return users[0]
    else:
        return None

def new_user(name, email, password):
    db.insert('cot_user',
        name=name,
        email=email,
        password=cotutil.hashpw(password)
    )

def set_user_password(name, password):
    db.update('cot_user',
        where="name=$name",
        vars={'name': name},
        password=cotutil.hashpw(password)
    )

def set_user_mailmode(name, mode):
    db.update('cot_user',
        where="name=$name",
        vars={'name': name},
        mailmode=mode
    )


# ============================================================================
# comments

def get_comment(id=None):
    comments = db.select('cot_comment',
        where="id=$id",
        vars=locals()
    )
    if comments:
        return comments[0]
    else:
        return None

def get_comments(viewer_name, item_host=None, item_path=None, item_name=None, item_user=None, user_name=None, limit=None):
    wheres = []
    if viewer_name:
        wheres.append("(private=false OR user_name=$viewer_name OR item_user=$viewer_name)")
    if item_host:
        wheres.append("(item_host=$item_host)")
    if item_path:
        wheres.append("(item_path=$item_path)")
    if item_name:
        wheres.append("(item_name=$item_name)")
    if item_user:
        wheres.append("(item_user=$item_user)")
    if user_name:
        wheres.append("(user_name=$user_name)")

    return db.select('cot_comment',
        where=" AND ".join(wheres),
        order="item_host, item_path, item_name, id",
        limit=limit,
        vars=locals()
    )

def get_pages(item_user, limit=None):
    return db.select('cot_comment',
        what="item_host, item_path, COUNT(id) AS comments",
        where='item_user=$item_user',
        group='item_host, item_path',
        limit=limit,
        vars={'item_user': item_user}
    )

def new_comment(user_name, item_host, item_path, item_name, content, item_user):
    db.insert('cot_comment',
        item_user=item_user,
        item_host=item_host,
        item_path=item_path,
        item_name=item_name,
        content=content,
        user_name=user_name
    )

def del_comment(id):
    db.delete('cot_comment',
        where="id=$id",
        vars=locals()
    )


# ============================================================================
# messages

def get_messages(user_name, limit=None):
    return db.select('cot_message',
        where="user_to = $user_name",
        vars={'user_name': user_name},
        limit=limit
    )

def new_message(user_from, user_to, content):
    db.insert('cot_message',
        user_from = user_from,
        user_to = user_to,
        content = content
    )
