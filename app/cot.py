#!/usr/bin/python

import web
import model
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
    '/comment/new', 'comment_new',
    '/comment/(.*)', 'comment',

    '/pm/new', 'pm_new',

    '/user/(.*)', 'user'
)
app = web.application(urls, globals())
app.add_processor(override_method)


if web.config.get('_session') is None:
    import rediswebpy
    session = web.session.Session(app, rediswebpy.RedisStore(prefix='session:cot:'), {
        'user': User(model.get_user(name="Anonymous")),
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
    'flash_clear': flash_clear,
    'urlquote': web.urlquote
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
        if id:
            comment = model.get_comment(id)
            return render.comment_list([comment], form)
        else:
            inp = web.input(item_host=None, item_path=None, item_name=None)
            related_pages = []
            related_items = []
            if inp.item_host and inp.item_path and inp.item_name:
                related_pages = model.db.select('cot_comment',
                    what="DISTINCT item_path AS page",
                    where="(item_host=$item_host)",
                    order="item_path",
                    limit=20,
                    vars={'item_host': inp.item_host}
                )
                related_items = model.db.select('cot_comment',
                    what="DISTINCT item_name AS item",
                    where="(item_host=$item_host) AND (item_path=$item_path)",
                    order="item_name",
                    limit=20,
                    vars={'item_host': inp.item_host, 'item_path': inp.item_path}
                )
            elif inp.item_host and inp.item_path:
                related_pages = model.db.select('cot_comment',
                    what="DISTINCT item_path AS page",
                    where="(item_host=$item_host)",
                    order="item_path",
                    limit=20,
                    vars={'item_host': inp.item_host}
                )
                related_items = model.db.select('cot_comment',
                    what="DISTINCT item_name AS item",
                    where="(item_host=$item_host) AND (item_path=$item_path)",
                    order="item_name",
                    limit=20,
                    vars={'item_host': inp.item_host, 'item_path': inp.item_path}
                )
            comments = model.get_comments(session.user.name, item_host=inp.item_host, item_path=inp.item_path, item_name=inp.item_name)
            return render.comment_list(comments, inp, related_pages, related_items)

    def DELETE(self, id):
        comment = model.get_comment(id)
        if comment:
            if session.user.name != "Anonymous" and (comment.item_user == session.user.name or comment.user_name == session.user.name):
                model.del_comment(id)
                flash("success", "Comment deleted")
            else:
                flash("error", "Permission denied")
        else:
            flash("error", "Comment not found")

        referer = web.ctx.env.get('HTTP_REFERER', 'http://www.commentonthis.net/')
        raise web.seeother(referer)


class comment_new:
    def GET(self, id=None):
        inp = web.input(quote=None, item_user=None, item_host=None, item_path=None, item_name=None)
        return render.comment_new(inp.quote, inp.item_user, inp.item_host, inp.item_path, inp.item_name)

    def POST(self):
        inp = web.input(close_after=False, item_host=None, item_path=None, item_name=None, content=None, item_user=None)

        model.new_comment(session.user.name, inp.item_host, inp.item_path, inp.item_name, inp.content, inp.item_user)

        page_owner = model.get_user(name=inp.item_user)
        if page_owner.mailmode == "all":
            web.sendmail(
                'Comment on This! <shish+cot@shishnet.org>',
                page_owner.email,
                '[CoT] New comment on '+get_domain(inp.item_host),
                session.user.name+" posted a comment on "+inp.item_host+inp.item_path+"#"+inp.item_name+":"+
                "\n\n"+inp.content+
                "\n\n    -- The Comment on This Team"
            )

        if inp.close_after:
            return render.comment_thanks()
        else:
            raise web.seeother(
                "/comment"+
                "?item_host="+web.urlquote(inp.item_host)+
                "&item_path="+web.urlquote(inp.item_path)+
                "&item_name="+web.urlquote(inp.item_name)
            )

class dashboard:
    def GET(self):
        if session.user.name == "Anonymous":
            raise web.seeother("/dashboard/login")
        pages = model.get_pages(item_user=session.user.name, limit=10)
        comments_on = model.get_comments(session.user.name, item_user=session.user.name, limit=5)
        comments_by = model.get_comments(session.user.name, user_name=session.user.name, limit=5)
        private_messages = model.get_messages(session.user.name, limit=5)
        return render.dashboard(session.user.name, pages, comments_on, comments_by, private_messages)

class dashboard_new:
    def GET(self):
        return render.dashboard_new()

    def POST(self):
        inp = web.input(name=None, email=None, password1=None, password2=None)

        if inp.password1 != inp.password2:
            return render.dashboard_new(error="Passwords don't match")

        if model.get_user(name=inp.name):
            return render.dashboard_new(error="Username taken")

        if model.get_user(email=inp.email):
            return render.dashboard_new(error="A user already has that address")

        model.new_user(inp.name, inp.email, inp.password1)
        session.user = User(model.get_user(name=inp.name, password=inp.password1))

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
        inp = web.input(name=None, password=None, return_to="/dashboard")

        if not inp.name or not inp.password:
            return render.dashboard_login(inp.name, "Missing name or password")

        user = model.get_user(name=inp.name, password=inp.password)

        if not user:
            return render.dashboard_login(inp.name, "No user with those details")

        session.user = User(user)

        go_to = web.cookies().get("login-redirect", "/dashboard")
        web.setcookie("login-redirect", "", expires=-1)
        raise web.seeother(go_to)

class dashboard_logout:
    def POST(self):
        inp = web.input(return_to=web.ctx.env.get('HTTP_REFERER', '/'))
        session.user = User(model.get_user(name="Anonymous"))
        raise web.seeother(inp.return_to)

class dashboard_reset:
    def GET(self):
        return render.dashboard_reset()

    def POST(self):
        inp = web.input(name=None, email=None)

        if not inp.name and not inp.email:
            return render.dashboard_reset(error="Missing name or email")

        user = model.get_user(name=inp.name) or model.get_user(email=inp.email)

        if not user or user.name == "Anonymous":
            return render.dashboard_login(error="No user with those details")

        pw = generate_password()
        model.set_user_password(user.name, pw)
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
        if session.user.name == "Anonymous":
            raise web.seeother("/dashboard/login")

        return render.settings()

    def POST(self):
        if session.user.name == "Anonymous":
            raise web.seeother("/dashboard/login")

        function = web.input(function=None).function

        if function == "setpw":
            inp = web.input(password=None, password1=None, password2=None)
            current = model.get_user(name=session.user.name, password=inp.password)
            if not current:
                flash("error", "Current password incorrect")
            elif inp.password1 != inp.password2:
                flash("error", "New passwords don't match")
            else:
                model.set_user_password(session.user.name, inp.password1)
                flash("success", "Password changed")

        if function == "setmailmode":
            inp = web.input(mailmode=None)
            if inp.mailmode in ["none", "daily", "all"]:
                # FIXME: argh at the DB and session not being as one...
                model.set_user_mailmode(session.user.name, inp.mailmode)
                session.user.mailmode = inp.mailmode
                flash("success", "Mail mode set to '%s'" % inp.mailmode)
            else:
                flash("error", "Invalid mail mode")

        raise web.seeother("/settings")


class user:
    def GET(self, name=None):
        user = model.get_user(name=name)
        pages = model.get_pages(item_user=user.name)
        comments_on = model.get_comments(session.user.name, item_user=user.name)
        comments_by = model.get_comments(session.user.name, user_name=user.name)
        return render.user(user.name, pages, comments_on, comments_by)


class pm_new:
    def POST(self):
        if session.user.name == "Anonymous":
            return render.error("Anonymous can't send private messages")

        inp = web.input(user_to=None, content=None)
        if not inp.user_to or not inp.content:
            return render.error("Message needs a target and some text")

        model.new_message(session.user.name, inp.user_to, inp.content)

        flash("success", "Message sent")

        raise web.seeother("/user/"+inp.user_to)

if __name__ == "__main__":
    app.run()
