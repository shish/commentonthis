
import web
import hashlib
import random
import re


def override_method(handler):
    web.ctx.method = web.input().get("_method", web.ctx.method)
    return handler()


class User:
    def __init__(self, row):
        self.name = row.name
        self.password = row.password
        self.email = row.email
        self.mailmode = row.mailmode
        self.avatar = "http://www.gravatar.com/avatar/"+hashlib.md5(row.email).hexdigest()


def hashpw(pw):
    return hashlib.sha1("salty-walty\x00"+pw).hexdigest()


def is_active_page(url):
    actives = [
        "user",
        "comment",
    ]
    for active in actives:
        if "commentonthis.net/"+active in url:
            return True
    return False


def generate_password():
    choices = "235679abcdefghkmnpqrstuvwxyz"
    pw = ""
    for n in range(0, 8):
        pw = pw + random.choice(choices)
    return pw


def shorten_url(url):
    return re.sub("https?://(www\.)?", "", url)


def shorten_datetime(dt):
    return str(dt)[:16]


def get_domain(url):
    return re.sub("https?://(?:www\.)?([^/]+).*", "\\1", url)
