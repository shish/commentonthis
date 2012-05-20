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
    '/comment', 'comment',
    '/comment/(.*)', 'comment',
    '/user/login', 'user_login',
    '/user/logout', 'user_logout',
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
            return render.new(inp.quote, inp.page_owner, inp.page_url, inp.item_id)
        elif id:
            comment = model.get_comment(id)
            return render.comment(comment, form)
        else:
            inp = web.input(page_url=None, item_id=None)
            comment = model.get_comments(session.user.id, inp.page_url, inp.item_id)
            form = self.form()
            return render.list(comment, form)

    def POST(self):
        """ Add new entry """
        form = self.form()
        inp = web.input(ajax=None)

        if not form.validates():
            raise web.seeother('/')

        page_owner_id = model.get_user(form.d.page_owner).id
        model.new_comment(page_owner_id, form.d.page_url, form.d.item_id, form.d.content)

        if inp.ajax:
            return json.dumps({"status": "ok", "message": "Comment submitted successfully", "data": {}})
        else:
            #referer = web.ctx.env.get('HTTP_REFERER', 'http://www.commentonthis.net/')
            #raise web.seeother(referer)
            return render.thanks()

    def DELETE(self, id):
        comment = model.del_comment(id)
        raise web.seeother('/')


class user_login:
    def GET(self):
        ret = web.ctx.env.get('HTTP_REFERER', '/')
        if "commentonthis.net" not in ret:
            ret = "/"
        return render.login(ret)

    def POST(self):
        inp = web.input(username=None, password=None, return_to=None)

        if inp.username and inp.password:
            user = model.get_user(username=inp.username, password=inp.password)
        else:
            return render.login(inp.return_to, inp.username, "Missing username or password")

        if user:
            session.user = User(user)
            if inp.return_to:
                raise web.seeother(inp.return_to)
            else:
                raise web.seeother("/user/%s" % (u.username, ))
        else:
            return render.login(inp.return_to, inp.username, "No user with those details")

    def DELETE(self):
        inp = web.input(return_to=web.ctx.env.get('HTTP_REFERER', '/'))
        session.user = User(model.get_user(username="Anonymous"))
        raise web.seeother(inp.return_to)


class user:
    def GET(self, id=None):
        return render.profile(id)


if __name__ == "__main__":
    app.run()
