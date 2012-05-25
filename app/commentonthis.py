#!/usr/bin/python

import web
import model
import json
import hashlib
from cotutil import *

web.config.debug = True

urls = (
    '/', 'about',
    '/about/(.*)', 'about',

    '/dashboard', 'dashboard',
    '/dashboard/new', 'dashboard_new',
    '/dashboard/login', 'dashboard_login',
    '/dashboard/logout', 'dashboard_logout',
    '/dashboard/reset', 'dashboard_reset',

    '/settings', 'settings',

    '/comment', 'comment',
    '/comment/(.*)', 'comment',

    '/pm/new', 'pm_new',

    '/user/(.*)', 'user'
)
app = web.application(urls, globals())
app.add_processor(override_method)


if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DBStore(model.db, 'session'), {
        'user': User(model.get_user(username="Anonymous")),
        'flash': [],
    })
    web.config._session = session
else:
    session = web.config._session

def flash(type, msg):
    session.flash.append((type, msg))

def flash_clear():
    session.flash = []

render = web.template.render('../templates', base='base', globals={
    'session': session,
    'shorten_url': shorten_url,
    'shorten_datetime': shorten_datetime,
    'get_domain': get_domain,
    'flash_clear': flash_clear
})



class about:
    def GET(self, page="index"):
        if page == "index":
            return render.about_index()
        if page == "demo":
            return render.about_demo()
        if page == "get-started":
            return render.about_get_started()


class comment:
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
            return render.comment_list(comments, inp)

    def POST(self):
        """ Add new entry """
        inp = web.input(close_after=False, page_owner=None, page_url=None, item_id=None, content=None)

        page_owner = model.get_user(username=inp.page_owner)
        model.new_comment(page_owner.id, inp.page_url, inp.item_id, inp.content, session.user.id)

        if page_owner.mailmode == "all":
            web.sendmail(
                'Comment on This! <shish+cot@shishnet.org>',
                user.email,
                '[CoT] New comment on '+inp.page_url,
                session.user.username+" posted a comment on "+inp.page_url+"#"+inp.item_id+":"+
                "\n\n"+inp.content+
                "\n\n    -- The Comment on This Team"
            )

        if inp.close_after:
            return render.comment_thanks()
        else:
            raise web.seeother("/comment?page_url="+inp.page_url+"&item_id="+inp.item_id)

    def DELETE(self, id):
        comment = model.get_comment(id)
        if comment:
            if session.user.username != "Anonymous" and (comment.page_owner_id == session.user.id or comment.commenter_id == session.user.id):
                model.del_comment(id)
                flash("success", "Comment deleted")
            else:
                flash("error", "Permission denied")
        else:
            flash("error", "Comment not found")

        referer = web.ctx.env.get('HTTP_REFERER', 'http://www.commentonthis.net/')
        raise web.seeother(referer)


class dashboard:
    def GET(self):
        if session.user.username == "Anonymous":
            raise web.seeother("/dashboard/login")
        pages = model.get_pages(page_owner_id=session.user.id, limit=10)
        comments_on = model.get_comments(session.user.id, page_owner_id=session.user.id, limit=5)
        comments_by = model.get_comments(session.user.id, commenter_id=session.user.id, limit=5)
        private_messages = model.get_messages(session.user.id, limit=5)
        return render.dashboard(session.user.username, pages, comments_on, comments_by, private_messages)

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

        go_to = web.cookies().get("login-redirect", "/dashboard")
        web.setcookie("login-redirect", "", expires=-1)
        raise web.seeother(go_to)

class dashboard_login:
    def GET(self):
        if not web.cookies().get("login-redirect"):
            ref = web.ctx.env.get('HTTP_REFERER')
            # if interaction-pages of this site, return to interaction page
            # if remote site, or info-pages of this site, go do dashboard
            if ref and is_active_page(ref):
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

        go_to = web.cookies().get("login-redirect", "/dashboard")
        web.setcookie("login-redirect", "", expires=-1)
        raise web.seeother(go_to)

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


class settings:
    def GET(self):
        if session.user.username == "Anonymous":
            raise web.seeother("/dashboard/login")

        return render.settings()

    def POST(self):
        if session.user.username == "Anonymous":
            raise web.seeother("/dashboard/login")

        function = web.input(function=None).function

        if function == "setpw":
            inp = web.input(password=None, password1=None, password2=None)
            current = model.get_user(username=session.user.username, password=inp.password)
            if not current:
                flash("error", "Current password incorrect")
            elif inp.password1 != inp.password2:
                flash("error", "New passwords don't match")
            else:
                model.set_user_password(session.user.username, inp.password1)
                flash("success", "Password changed")

        if function == "setmailmode":
            inp = web.input(mailmode=None)
            if inp.mailmode in ["none", "daily", "all"]:
                # FIXME: argh at the DB and session not being as one...
                model.set_user_mailmode(session.user.username, inp.mailmode)
                session.user.mailmode = inp.mailmode
                flash("success", "Mail mode set to '%s'" % inp.mailmode)
            else:
                flash("error", "Invalid mail mode")

        raise web.seeother("/settings")


class user:
    def GET(self, id=None):
        pages = model.get_pages(page_owner_id=session.user.id)
        comments_on = model.get_comments(session.user.id, page_owner_id=session.user.id)
        comments_by = model.get_comments(session.user.id, commenter_id=session.user.id)
        return render.user(id, pages, comments_on, comments_by)


class pm_new:
    def POST(self):
        if session.user.username == "Anonymous":
            return render.error("Anonymous can't send private messages")

        inp = web.input(user_to=None, content=None)
        if not inp.user_to or not inp.content:
            return render.error("Message needs a target and some text")

        model.new_message(session.user.id, model.get_user(username=inp.user_to).id, inp.content)

        flash("success", "Message sent")

        raise web.seeother("/user/"+inp.user_to)

if __name__ == "__main__":
    app.run()
