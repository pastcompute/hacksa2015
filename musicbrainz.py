#!/usr/bin/python
import sqlite3
import musicbrainzngs
import json
import urllib
import sys


musicbrainzngs.set_useragent("phaze.space hacksa2015 prototype", "0.1")


conn = sqlite3.connect('charts2.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS musicbrainz_recording (id integer primary key autoincrement,song_id integer, musicbrainz_recording text)')
c.execute('create table if not exists musicbrainz_failure (song_id integer, last_try timestamp)')
c.execute('create table if not exists aci(song_id integer, bpm float,key text,scale text);')
conn.commit()


c.execute('select id,name, artist from song where id not in (select song_id from musicbrainz_recording) and id not in (select song_id from musicbrainz_failure where last_try > strftime(\'%s\',\'now\',\'-7 days\') group by song_id having count(song_id) < 5)')
rows=c.fetchall()

for row in rows:
   song_id=row[0]
   name=row[1]
   artist=row[2]
   mq = '"%s" AND artist:"%s"' % (name, artist)
   print 'searching musicbrainz for ' + repr(artist)+ ' - ' + repr(name)
   result = musicbrainzngs.search_recordings(query=mq, limit=10)
   first_mbtrackid = None
   for y in result['recording-list']:
      #if (result['recording-count']result['recording-count'] > 0:
      if 'id' in y:
         mbtrackid = y['id']   # <-- matches search results from https://musicbrainz.org/search?query=%22Are+You+Gonna+Go+My+Way%22+AND+artist%3A%22Lenny+Kravitz%22+AND+country%3AAU&type=recording&limit=25&method=advanced
         if first_mbtrackid is None:
            first_mbtrackid=mbtrackid
         rec = musicbrainzngs.get_recording_by_id(id=mbtrackid, includes=["tags"])
         url ='http://acousticbrainz.org/'+mbtrackid+'/low-level'
         print 'fetching from url: ' +url
         jsonurl = urllib.urlopen(url)
         if jsonurl.getcode() == 200:
            print '- has an acoustid entry'
            rawJson = json.loads(jsonurl.read())
            data= rawJson[u'lowlevel']
            rhythm=rawJson[u'rhythm']
            beats=rhythm[u'bpm']
            tonal=rawJson[u'tonal']
            key=tonal[u'chords_key']
            scale=tonal[u'chords_scale']
            print 'BPM: ' +repr(beats)
            c.execute('insert into stats(song_id,bpm,key,scale) values (?,?,?,?)',(song_id,beats,key,scale))
            conn.commit()
            break;
   if first_mbtrackid is not None:
      print ' saving mbid '
      c.execute('insert into musicbrainz_recording (song_id,musicbrainz_recording) values (?,?)',(song_id,mbtrackid))
      conn.commit()
   else:
      print ' song not found in musicbrainz ' 
      c.execute('insert into musicbrainz_failure (song_id,last_try) values (?,strftime(\'%s\',\'now\'))',(song_id,))
      conn.commit()

