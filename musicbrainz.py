import sqlite3
import musicbrainzngs
import json
import urllib
import sys


musicbrainzngs.set_useragent("phaze.space hacksa2015 prototype", "0.1")


conn = sqlite3.connect('charts2.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS musicbrainz_recording (id integer primary key autoincrement,song_id integer, musicbrainz_recording text)')
c.execute('create table if not exists bpm (song_id integer, bpm float);')
conn.commit()


c.execute('select id,name, artist from song where id not in (select song_id from musicbrainz_recording)')
rows=c.fetchall()
for row in rows:
   song_id=row[0]
   name=row[1]
   artist=row[2]
   mq = '"%s" AND artist:"%s"' % (name, artist)
   print 'searching musicbrainz for ' + repr(artist)+ ' - ' + repr(name)
   result = musicbrainzngs.search_recordings(query=mq, limit=5)
   mbtrackid = None
  
   for y in result['recording-list']:
      mbtrackid = y['id']   # <-- matches search results from https://musicbrainz.org/search?query=%22Are+You+Gonna+Go+My+Way%22+AND+artist%3A%22Lenny+Kravitz%22+AND+country%3AAU&type=recording&limit=25&method=advanced
      
      rel = y['release-list'][0]['id']
      rec = musicbrainzngs.get_recording_by_id(id=mbtrackid, includes=["tags"])
      url ='http://acousticbrainz.org/'+mbtrackid+'/low-level'
      print 'fetching from url: ' +url
      jsonurl = urllib.urlopen(url)
      if jsonurl.getcode() == 200:
         rawJson = json.loads(jsonurl.read())
         data= rawJson[u'lowlevel']
         rhythm=rawJson[u'rhythm']
         beats=rhythm[u'bpm']
         print 'BPM: ' +repr(beats)
         c.execute('insert into musicbrainz_recording (song_id,musicbrainz_recording) values (?,?)',(song_id,mbtrackid))
         c.execute('insert into bpm (song_id,bpm) values (?,?)',(song_id,beats))
         conn.commit()
         
         break;
         