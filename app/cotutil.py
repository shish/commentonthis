
import web
import hashlib


def override_method(handler):
    web.ctx.method = web.input().get("_method", web.ctx.method)
    return handler()


class User:
    def __init__(self, row):
        self.id = row.id
        self.username = row.username
        self.password = row.password
        self.email = row.email
        self.avatar = "http://www.gravatar.com/avatar/"+hashlib.md5(row.email).hexdigest()


def hashpw(pw):
    return hashlib.sha1("salty-walty-"+pw).hexdigest()
