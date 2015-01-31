#
# Entry point for phaze.space party-on proof of concept demo
#
#
# WARNING for some reason I cant work out how to not have the trailing slash
# e.g.
# http://localhost/~andrew/hacksa/www/demo.wsgi/
#

import web
import sys
import os

# Path relative to cwd
# On my computer this is ~/public_html
# But on the VPS this will need to be something else
db = web.database(dbn="sqlite", db="hacksa/charts.db")

render = web.template.render('hacksa/www/templates', cache=False) #WTF doesnt a relative path work?

urls = (
    '/diag', 'diag',
    '/(.*)', 'controller'
)

class diag:
    def GET(self):
      return "cwd=", os.getcwd()

class controller:
    def GET(self, egg):
        data = web.input()
        if 'demo' in data:
          return "Generate a playlist based on : " + data['wordlist']

        tagwords = [ 'rock', 'pop', 'dance' ]
        return render.index(egg, tagwords)   # index.html is the template
  
app = web.application(urls, globals())
# app.notfound = lambda: web.notfound(render.index('oops'))
# web.config.debug = False

if __name__ == "__main__":
    app.run()
else:
    application = app.wsgifunc()

# http://www.goat1000.com/tagcanvas-functions.php
# http://www.pcexcellence.ca/helpdesk/kb_article.php?ref=2036-QYSZ-5773
# We hacked bootstrap plugin tag cloud
# http://api.jquery.com/category/manipulation/
# http://www.w3schools.com/jsref/jsref_obj_string.asp
# http://webpy.org/cookbook/input
