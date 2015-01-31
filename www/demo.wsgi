#
# Entry point for phaze.space party-on proof of concept demo
#
#
# WARNING for some reason I cant work out how to not have the trailing slash
# e.g.
# http://localhost/~user/hacksa/www/demo.wsgi/
#
# Installing on the vultr vps:
#
# http://server/app
#
# THIS IS ONLY FOR THE HACKATHON, IT IS LIKELY INSECURE FOR A REAL PRODUCTION SYSTEM!
#
# Clone the git repo at /var/www --> /var/www/hacksa2015
# Copy phaze-space.conf --> /etc/apache2/sites-available
# Run `a2enmod wsgi`
# Run `a2enmod rewrite`
# Run `a2ensite phaze-space`
# Run `service apache2 restart`

import web
import sys
import os

render_relpath = '/var/www/hacksa2015/www'
db_relpath = '/var/www/hacksai2015'

# The following are for public_html on my PC
#render_relpath = 'hacksa/www'
#db_relpath = 'hacksa'

# Path relative to cwd
# On my computer this is ~/public_html
# But on the VPS this will need to be something else
db = web.database(dbn="sqlite", db=os.path.join(db_relpath, 'charts.db'))

render = web.template.render(os.path.join(render_relpath, 'templates'), cache=False) #WTF doesnt a relative path work?

urls = (
    '/diag', 'diag',
    '/(.*)', 'controller'
)

class diag:
    def GET(self):
      os.system('ls -la > /tmp/x')
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
