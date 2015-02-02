#!/usr/bin/python
# This is a simple python script to populate the chart, track and chart_pos tables from the V charts.
# 
import sqlite3

conn = sqlite3.connect('charts2.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS song (id integer primary key autoincrement,name text,artist text)')
c.execute('CREATE TABLE IF NOT EXISTS song_artists (song_id, artist_id)')
c.execute('CREATE TABLE IF NOT EXISTS artist (id integer primary key autoincrement,name text)')
conn.commit()

contains=(u' ft. ',u' &amp; ',u' feat. ',u' featuring ',u' ft ',u', ',u' & ')

def getArtistID(artistA):
   c.execute('select id from artist where name=?',(artistA,))
   artistID=-1
   res=c.fetchone()
   if res is None:
      c.execute('insert into artist (name) values (?)',(artistA,))
      artistID=c.lastrowid
      conn.commit()
   else:
      artistID=res[0]
   return artistID

def updateArtists(artist,song_id):
   # We need to deal with multiple artists on a track
   print 'processing artist  ' + artist + ' '+repr(song_id)
   beginIndex=0
   notFound=True
   for x in contains:
      index =artist[beginIndex:].find(x)
      if index > 0:
         tmp=artist[beginIndex:index]
         artistID=getArtistID(tmp)
         c.execute('insert into song_artists (song_id,artist_id) values (?,?)',(song_id,artistID))
         conn.commit()
         beginIndex=index+len(x)
         print 'added song artist ' + repr(song_id)+ ' '+repr(artistID)
         notFound=False
	 updateArtists(artist[beginIndex:],song_id);
	 return
   if notFound:
      tmp=artist[beginIndex:]
      print 'begin index '+repr(beginIndex) + ' ' +artist[beginIndex:] +' '+ tmp
      artistID=getArtistID(tmp)
      c.execute('insert into song_artists (song_id,artist_id) values (?,?)',(song_id,artistID))
      conn.commit()
      print 'added song artist ' + repr(song_id)+ ' '+repr(artistID)
   
  # artistID=getArtistID(artist)
#   c.execute('insert into song_artists (song_id,artist_id) values (?,?)',(song_id,artistID))
#
#   conn.commit()


c.execute('select track_id, song_id,name, artist from track where song_id is null');
rows=c.fetchall()
print rows
for row in rows:	
   trackID=row[0]
   songID=row[1]
   name=row[2].lower()
   artist=row[3].lower().replace('&amp;','&')
   c.execute('select id,name,artist from song where name=? and artist=?',(name,artist))
   res=c.fetchone()
   if res is None:
      c.execute('insert into song (name,artist) values (?,?)',(name,artist))
      conn.commit()
      songID=c.lastrowid
      updateArtists(artist,songID)
      c.execute('update track set song_id=? where track_id=?',(songID,trackID))
      conn.commit()
   else:
      songID=res[0]
      c.execute('update track set song_id=? where track_id=?',(songID,trackID))
      conn.commit()

