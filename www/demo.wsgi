#
# Entry point for phaze.space party-on proof of concept demo
#
# In case it is not evident to the causal reader, this code is a proof of concept jerry rigged
# one evening for a hackathon and I would not normally code this hacky for a real world
# or open source project!
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
import random

render_relpath = '/var/www/hacksa2015/www'
db_relpath = '/var/www/hacksa2015'

# The following are for public_html on my PC
#render_relpath = '/home/andrew/Mega/hacksa/www'
#db_relpath = '/home/andrew/Mega/hacksa'

# Path relative to cwd
# On my computer this is ~/public_html
# But on the VPS this will need to be something else
db = web.database(dbn="sqlite", db=os.path.join(db_relpath, 'charts.db'))

# Lots of ugly code to try and be a tag cloud generator
def magic_tag_cloud():
  qwords = db.select('genre')
  tagwords = [ ]
  for x in qwords:
    tagwords += [ x['name'].replace(" ",'') ]
  if len(tagwords) < 1:
    tagwords = [ 'rock', 'pop', 'dance' ]

  # TODO: Mash with other tables to build up much larger tag cloud
  # e.g. if a hit is in the top three of any chart then add its artist

  q2 = db.query( "select distinct hits.xid, hits.name, hits.artist  from hitsCharts left join hits where position <= 2 and hits.xid = hitsCharts.xid")
  for x in q2:
    artist = x['artist']
    tagwords += [ artist.replace(" ",'') ]

  return tagwords

# Lots of ugly code to try and be a magical playlist generator
def magic_build_playlist(tagwords):
  # For now fake it - just grab 5 hits from the top 100 and another 5 from the ARIA
  # Randomise the selection : just query the lot then pick out N random positions for now

  # There must be a better way, querying the length separately is not atomic...
  q1 = db.query( "select count(*) as N from hits H, charts C, hitsCharts X where C.name like '%ARIA%' and C.cid=X.cid and H.xid=X.xid")
  x1 = q1[0]['N']
  q2 = db.query( "select count(*) as N from hits H, charts C, hitsCharts X where C.name like '%Top 100%' and C.cid=X.cid and H.xid=X.xid")
  x2 = q2[0]['N']

  print >> sys.stderr, x1, x2

  q1 = db.query( "select H.* from hits H, charts C, hitsCharts X where C.name like '%ARIA%' and C.cid=X.cid and H.xid=X.xid")
  q2 = db.query( "select H.* from hits H, charts C, hitsCharts X where C.name like '%Top 100%' and C.cid=X.cid and H.xid=X.xid")
  list1 = random.sample(range(x1), min(x1,5))
  list2 = random.sample(range(x2), min(x2,5))

  # I'm pretty sure this can be done better or more Pythonic but its late and this works
  songs = []
  i=0
  for item in q1:
    i = i + 1
    if i-1 not in list1: continue
    p = dict()
    p['artist'] = item['artist']
    p['song'] = item['name']
    p['itunes'] = item['buy']
    songs += [ p ]
  # Randomise the selection : just query the lot then pick out N random positions for now
  i=0
  for item in q2:
    i = i + 1
    if i-1 not in list2: continue
    p = dict()
    p['artist'] = item['artist']
    p['song'] = item['name']
    p['itunes'] = item['buy']
    songs += [ p ]
  # Randomise the combined list and select 5 of them
  list3 = random.sample(range(len(songs)), min(len(songs),5))
  i=0
  result = []
  for item in songs:
    i = i + 1
    if i-1 not in list3: continue
    result += [item]

  return result

render = web.template.render(os.path.join(render_relpath, 'templates'), cache=False) #WTF doesnt a relative path work?

urls = (
    '/diag', 'diag',
    '/genre', 'genre',
    '/top3', 'top3',
    '/(.*)', 'controller'
)

class diag:
    def GET(self):
      os.system('ls -la > /tmp/x')
      return "cwd=", os.getcwd()

class genre:
    def GET(self):
      p = ""
      for x in tagwords:
        p = p + x + "\n"
      return p

class top3:
    def GET(self):
      p = ""
      for x in q2:
        p = p + repr(x) + "\n"
      return p

class controller:
    def GET(self, egg):
        data = web.input()
        if 'premium-features' in data:
          return render.premium()
        if 'demo' in data:
          # "Generate a playlist based on : " + data['wordlist']
          tagwords = data['wordlist']
          songs = magic_build_playlist(tagwords)
          if data['demo'].startswith('Click'):
            return render.playlist('aussie', songs)   # index.html is the template
          return render.playlist(egg, songs)   # index.html is the template

        tagwords = magic_tag_cloud()
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
