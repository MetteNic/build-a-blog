#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class MainBlog(Handler):
    """ Handles requests coming in to '/blog'
    """
    def render_main_blog(self, title="", body = "", error="", blogs =""):
        blogs=db.GqlQuery(" SELECT * FROM Blog"
                          " ORDER BY created DESC "
                          "limit 5")






        self.render("main_blog.html", title=title, body=body, error=error, blogs = blogs)

    def get(self):
        self.render_main_blog()




class NewPost(webapp2.RequestHandler):
    """ Handles requests coming in to '/newpost'"""
    def get(self):
        t = jinja_env.get_template("newpost.html")
        content = t.render(title=self.request.get("title"),
                           error=self.request.get("error"), body=self.request.get("body"))

        self.response.write(content)

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            b = Blog(title = title, body = body)
            b.put()
            id = b.key().id()

            self.redirect("/blog/" + str(id))
        else:
            error = "we need both a title and a body!"
            t = jinja_env.get_template("newpost.html")
            content = t.render(title=title,
                               error=error, body=body)


            self.response.write(content)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        post = Blog.get_by_id(int(id))
        if post:
            t = jinja_env.get_template("viewpost.html")
            content = t.render(title=post.title, body=post.body)
            self.response.write(content)
        else:
            error = "no such post"
            t = jinja_env.get_template("viewpost.html")
            content = t.render(error=error)
            self.response.write(content)






app = webapp2.WSGIApplication([
    ('/blog', MainBlog),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler,),
], debug=True)
