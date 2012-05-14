#!/usr/bin/python

import web
import model

render = web.template.render('../templates', base='base')
urls = (
    '/comments', 'comments',
    '/comment/(.*)', 'comment',
    '/(.*)', 'hello'
)
app = web.application(urls, globals())

def override_method(handler):
    web.ctx.method = web.input().get("_method", web.ctx.method)
    return handler()

app.add_processor(override_method)


class hello:
    def GET(self, name):
        if not name:
            name = 'World'
        return 'Hello, ' + name + '!'


class comments:
    form = web.form.Form(
        web.form.Textbox('page_owner', web.form.notnull, description="Page Owner:"),
        web.form.Textbox('page_url', web.form.notnull, description="Page URL:"),
        web.form.Textbox('item_id', web.form.notnull, description="Item ID:"),
        web.form.Textbox('content', web.form.notnull, description="Comment:"),
        web.form.Button('Add todo'),
    )

    def GET(self):
        comments = model.get_comments()
        form = self.form()
        return render.list(comments, form)

    def POST(self):
        """ Add new entry """
        form = self.form()
        if not form.validates():
            raise web.seeother('/')
        page_owner_id = 0 # form.d.page_owner
        model.new_comment(page_owner_id, form.d.page_url, form.d.item_id, form.d.content)
        raise web.seeother('/')


class comment:
    def GET(self, id):
        comments = model.get_comment(id)
        return render.comment(comments, form)

    def DELETE(self, id):
        comments = model.del_comment(id)
        raise web.seeother('/')

if __name__ == "__main__":
    app.run()
