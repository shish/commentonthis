
import web
import hashlib
import random
import re
import bcrypt


def override_method(handler):
    web.ctx.method = web.input().get("_method", web.ctx.method)
    return handler()


class DefaultingSession(web.session.Session):
    def _save(self):
        current_values = dict(self)
        del current_values['session_id']
        del current_values['ip']

        cookie_name = self._config.cookie_name
        cookie_domain = self._config.cookie_domain
        if not self.get('_killed') and current_values != self._initializer:
            web.setcookie(cookie_name, self.session_id, domain=cookie_domain)
            self.store[self.session_id] = dict(self)
        else:
            if web.cookies().get(cookie_name):
                web.setcookie(cookie_name, self.session_id, expires=-1, domain=cookie_domain)


def hashpw(password):
    return bcrypt.hashpw(password, bcrypt.gensalt())

def pwmatch(password, digest):
    return bcrypt.hashpw(password, digest) == digest


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
