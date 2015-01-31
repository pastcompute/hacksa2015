# Test harness to parse a Channel-V URL from JSON
#
# This runs in current directory and builds charts.db
# Which will be used by the web app
#
# Example input:
# {
# Date: "2015-01-20",
# Description: "Top 100 Most Iconic 90's Anthems Ever",
# Name: "Top 100 Most Iconic 90s Anthems Ever",
# id: null,
# Tracks: [
# {
# Artist: "Hanson",
# Buy: "https://itunes.apple.com/au/album/mmmbop/id91888154?i=91888157&uo=4&at=1l3voVS",  <-- may be null
# Date: null,     <-- often zero
# Name: "mmmbop",
# id: 13462,
# Position: "100" <-- sometimes not present
# },
#
#

# Another alternative:
#import requests
#r = requests.get('someurl')
#print r.json() # if response type was set to JSON, then you'll automatically have 

import json
import urllib
import pprint
import sys
from musicbrainzngs import caa

# url = "http://localhost/~andrew/hacksa2015/MostPlayedOnAir_MAX"

if len(sys.argv) > 1:
  url = sys.argv[1]
else:
  print "Please specify URL"
  sys.exit(0)

jsonurl = urllib.urlopen(url)

rawChart = json.loads(jsonurl.read())

import itunes
from urlparse import urlparse, parse_qs

if not itunes.is_caching_enabled():
  itunes.enable_caching('/tmp/itunes_cache')

import musicbrainzngs
musicbrainzngs.set_useragent("phaze.space hacksa2015 prototype", "0.1")

#for x in text['Tracks']:  print x

# What do we want to do with this?

# a. Dump as a nice pretty TUI table
# b. Convert to sqlite
# c. Convert to something I can load into tulip

from tabulate import tabulate
justtracks = dict()
datatracks = dict()
for x in rawChart['Tracks']:
  tid = x[u'id']
  item = dict(x)
  del item[u'Date']   # always 0 for some reason, just drop it
  del item[u'Buy']   # Clutters the table. tabulate I dont know how to order they keys
  justtracks[tid] = item
  item2 = dict(x)
  del item2[u'Date']
  #del item2[u'id']
  #item2[u'id'] = int(tid)
  datatracks[tid] = item2

#print tabulate(justtracks.values(), headers="keys")

import sqlite3
conn = sqlite3.connect('charts.db')
c = conn.cursor()
# SELECT name FROM sqlite_master WHERE type='table' AND name='table_name';
# c.execute('DROP TABLE IF EXISTS hits')
c.execute('CREATE TABLE IF NOT EXISTS hits (xid integer primary key not null, artist text, name text, buy text, igenre text, mbz text, mbtags text)')
c.execute('CREATE TABLE IF NOT EXISTS charts (cid integer primary key autoincrement, date text, description text, name text)')
# A hit can be in multiple charts
c.execute('CREATE TABLE IF NOT EXISTS hitsCharts (xid integer, cid integer, position integer, primary key (xid, cid))')
c.execute('CREATE TABLE IF NOT EXISTS genre (name text, primary key(name))')


# Generate cid somehow...
# because the id specified is null
# Really because we dont want to duplicate stuff unnecessarily
# So lets go with the name & date, if they are same assume this is a re-import
# We just use cid internally for join
# Except date is sometimes bogus as well

chartName = rawChart['Name']
chartDate = rawChart['Date']
#c.execute("select cid, date from charts where name = ? and date = ?", ( chartName, chartDate ))
c.execute("select cid from charts where name = ?", ( chartName, ))
result = c.fetchone()
if result is not None:
  print "This chart already imported. Checking hits..."
else:
  c.execute("INSERT INTO charts (date,description,name) VALUES (?,?,?)", (chartDate, rawChart['Description'], chartName))

c.execute("select cid from charts where name = ?", ( chartName, ))
result = c.fetchone()
cid = result[0]

for x in datatracks.values():
  # FIXME handle CTRL+C in this loop
  # Escape single quotes using mappings
  xid = x['id']
  tune = x['Buy']
  xartist = x['Artist']
  xtitle = x['Name']
  position = None
  if 'Position' in x:
    position = int(x['Position'])
  song = None
  genre = None
  if tune is not None and len(tune) > 0 :
    o = urlparse(tune)
    q = parse_qs(o.query)
    qid = q['i'][0]
    try:
      song = itunes.lookup(qid)
    except:
      # try last part of path instead
      #print "Will try id... ; Not found: " , qid, tune
      q = o.path.split("/")[-1]
      qid = q.split("id")[1]
      try:
        song = itunes.lookup(qid)
      except:
        print "Not found in itunes lookup: " , qid, tune
        pass
    if song is not None:
      genre = song.get_genre()

  # Man this code is fugly... never put a hackathon into production!

  mq = '"%s" AND artist:"%s" AND country:AU' % (xtitle, xartist)
  # Just get the first. For the purpose of this proof of concept, we dont care if it is a bit wrong
  # Problem is we need to find first with AU somehow, fallback to US
  print mq
  result = musicbrainzngs.search_recordings(query=mq, limit=5)
  #pprint.pprint(result['recording-list'][0])
  mbtags = None
  for y in result['recording-list']:
    mbtrackid = y['id']   # <-- matches search results from https://musicbrainz.org/search?query=%22Are+You+Gonna+Go+My+Way%22+AND+artist%3A%22Lenny+Kravitz%22+AND+country%3AAU&type=recording&limit=25&method=advanced

    rel = y['release-list'][0]['id']
    rec = musicbrainzngs.get_recording_by_id(id=mbtrackid, includes=["tags"])
    tags = []
    print 'R:', rec['recording']
    if 'tag-list' in rec['recording']:
      for t in rec['recording']['tag-list']:
        atag = t['name']
        try:
          c.execute("INSERT INTO genre (name) VALUES (?)", atag)
        except:
          pass

        tags += [atag]
      mbtags = ",".join(tags) # This is possibly where nosql may help...
      print mbtags
    coverart = None
    try:
      coverart = caa.get_image_list(webid)
    except:
      pass
    break # just the first

  print 'update'

  c.execute("select xid, artist, name from hits where xid = ?", ( xid, ))
  result = c.fetchone()
  if result is not None:
    # we have this already
    # in proper version, double check name mismatches, etc.
    print "Dupe hit ignored"
    pass
  else:
    c.execute("INSERT INTO hits (xid,artist,name,buy,igenre, mbz, mbtags) VALUES (?,?,?,?,?,?,?)", (xid, xartist, xtitle, tune, genre, mbtrackid, mbtags))

  try:
    c.execute("INSERT INTO hitsCharts(xid,cid,position) VALUES (?,?,?)", (xid, cid,position))
  except:
    print "Dupe hit chart ignored"
    pass

conn.commit()

c.execute("select igenre, count(*) from hits group by igenre")
result = c.fetchall()

print tabulate(result)

c.close()

# sqlite3 charts.db 'select * from hits'

# Now we do magic stuff based on keyword, genre
# Mash with the itunes link if present

# TO avoid hammering for now just do first one found
# Split the buy URL: https://itunes.apple.com/au/album/greek-tragedy/id952479484?i=952479487&uo=4&at=1l3voVS

# Wraps http://www.apple.com/itunes/affiliates/resources/documentation/itunes-store-web-service-search-api.html


#o = urlparse(itunestest)
#q = parse_qs(o.query)
#qid = q['i'][0]
##qid = 475390461
#print qid
#album = itunes.lookup(qid)
#print "%s -> %s" % (itunesartist, album.get_artist())
#print "Genre -> %s" % album.get_genre()


# So now we can keyword search the genre artist name and title

# Do some smart synonym stuff when searching for common terms

# Do some googling to help build up word lists 
