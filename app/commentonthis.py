#!/usr/bin/python

import web
import model
import json
import hashlib
from cotutil import *

web.config.debug = True

urls = (
    '/', 'index',
    '/demo', 'demo',

    '/dashboard', 'dashboard',
    '/dashboard/new', 'dashboard_new',
    '/dashboard/login', 'dashboard_login',
    '/dashboard/logout', 'dashboard_logout',
    '/dashboard/reset', 'dashboard_reset',
    '/dashboard/setpw', 'dashboard_setpw',

    '/comment', 'comment',
    '/comment/(.*)', 'comment',

    '/user/(.*)', 'user'
)
app = web.application(urls, globals())
app.add_processor(override_method)


if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DBStore(model.db, 'session'), {
        'user': User(model.get_user(username="Anonymous"))
    })
    web.config._session = session
else:
    session = web.config._session

render = web.template.render('../templates', base='base', globals={'session': session})


class index:
    def GET(self):
        return render.index()


class demo:
    def GET(self):
        return render.demo()


class comment:
    form = web.form.Form(
        web.form.Textbox('page_owner', web.form.notnull, description="Page Owner:"),
        web.form.Textbox('page_url', web.form.notnull, description="Page URL:"),
        web.form.Textbox('item_id', web.form.notnull, description="Item ID:"),
        web.form.Textbox('content', web.form.notnull, description="Comment:"),
        web.form.Button('Add Comment'),
    )

    def GET(self, id=None):
        if id == "new":
            inp = web.input(quote=None, page_owner=None, page_url=None, item_id=None)
            return render.comment_new(inp.quote, inp.page_owner, inp.page_url, inp.item_id)
        elif id:
            comment = model.get_comment(id)
            return render.comment_list([comment], form)
        else:
            inp = web.input(page_url=None, item_id=None)
            comments = model.get_comments(session.user.id, inp.page_url, inp.item_id)
            form = self.form()
            return render.comment_list(comments, form)

    def POST(self):
        """ Add new entry """
        form = self.form()
        inp = web.input(ajax=None)

        if not form.validates():
            raise web.seeother('/')

        page_owner_id = model.get_user(username=form.d.page_owner).id
        model.new_comment(page_owner_id, form.d.page_url, form.d.item_id, form.d.content)

        if inp.ajax:
            return json.dumps({"status": "ok", "message": "Comment submitted successfully", "data": {}})
        else:
            #referer = web.ctx.env.get('HTTP_REFERER', 'http://www.commentonthis.net/')
            #raise web.seeother(referer)
            return render.comment_thanks()

    def DELETE(self, id):
        comment = model.del_comment(id)
        raise web.seeother('/')


class dashboard:
    def GET(self):
        if session.user.username == "Anonymous":
            raise web.seeother("/dashboard/login")
        pages = model.get_pages(page_owner_id=session.user.id)
        return render.dashboard(session.user.username, pages)

class dashboard_new:
    def GET(self):
        return render.dashboard_new()

    def POST(self):
        inp = web.input(username=None, email=None, password1=None, password2=None)

        if inp.password1 != inp.password2:
            return render.dashboard_new(error="Passwords don't match")

        if model.get_user(username=inp.username):
            return render.dashboard_new(error="Username taken")

        if model.get_user(email=inp.email):
            return render.dashboard_new(error="A user already has that address")

        model.new_user(inp.username, inp.email, inp.password1)
        session.user = User(model.get_user(username=inp.username, password=inp.password1))
        raise web.seeother(web.cookies().get("login-redirect", "/dashboard"))

class dashboard_login:
    def GET(self):
        if not web.cookies().get("login-redirect"):
            ref = web.ctx.env.get('HTTP_REFERER')
            # if interaction-pages of this site, return to interaction page
            # if remote site, or info-pages of this site, go do dashboard
            if is_active_page(ref):
                web.setcookie("login-redirect", ref, 60*15)
            else:
                web.setcookie("login-redirect", "/dashboard", 60*15)
        return render.dashboard_login()

    def POST(self):
        inp = web.input(username=None, password=None, return_to="/dashboard")

        if not inp.username or not inp.password:
            return render.dashboard_login(inp.username, "Missing username or password")

        user = model.get_user(username=inp.username, password=inp.password)

        if not user:
            return render.dashboard_login(inp.username, "No user with those details")

        session.user = User(user)
        raise web.seeother(web.cookies().get("login-redirect", "/dashboard"))

class dashboard_logout:
    def POST(self):
        inp = web.input(return_to=web.ctx.env.get('HTTP_REFERER', '/'))
        session.user = User(model.get_user(username="Anonymous"))
        raise web.seeother(inp.return_to)

class dashboard_reset:
    def GET(self):
        return render.dashboard_reset()

    def POST(self):
        inp = web.input(username=None, email=None)

        if not inp.username and not inp.email:
            return render.dashboard_reset(error="Missing username or email")

        user = model.get_user(username=inp.username) or model.get_user(email=inp.email)

        if not user or user.username == "Anonymous":
            return render.dashboard_login(error="No user with those details")

        pw = generate_password()
        model.set_user_password(user.username, pw)
        web.sendmail(
            'Comment on This! <shish+cot@shishnet.org>',
            user.email,
            '[CoT] Password Reset',
            "Your new password is "+pw+
            "\n\nLog in at http://www.commentonthis.net/dashboard/login"+
            "\n\nSee you in a moment!"+
            "\n\n    -- The Comment on This Team"
        )

        return render.dashboard_reset_sent()

class dashboard_setpw:
    def POST(self):
        inp = web.input(password=None, password1=None, password2=None)

        current = model.get_user(username=session.user.username, password=inp.password)
        if not current:
            return render.error("Current password incorrect")

        if inp.password1 != inp.password2:
            return render.error("New passwords don't match")

        model.set_user_password(session.user.username, inp.password1)

        raise web.seeother("/dashboard")


class user:
    def GET(self, id=None):
        pages = model.get_pages(page_owner_id=session.user.id)
        return render.user(id, pages)


if __name__ == "__main__":
    app.run()
