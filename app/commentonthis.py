#!/usr/bin/python

import web
import model
import json

web.config.debug = True

def override_method(handler):
    web.ctx.method = web.input().get("_method", web.ctx.method)
    return handler()

urls = (
    '/', 'index',
    '/demo', 'demo',
    '/comments', 'comments',
    '/comments/(.*)', 'comments'
)
app = web.application(urls, globals())
app.add_processor(override_method)

if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('../sessions'), {'username': 'Anonymous'})
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


class comments:
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
            comments = model.get_comment(id)
            return render.comment(comments, form)
        else:
            comments = model.get_comments()
            form = self.form()
            return render.list(comments, form)

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
        comments = model.del_comment(id)
        raise web.seeother('/')


if __name__ == "__main__":
    app.run()
