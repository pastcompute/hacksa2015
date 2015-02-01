#!/usr/bin/python
# This is a simple python script to populate the chart, track and chart_pos tables from the V charts.
# 
import json
import urllib
import sys

if len(sys.argv) > 1:
  url = sys.argv[1]
else:
  print "Please specify URL"
  sys.exit(0)

# Create the database first thing before we use it
import sqlite3
conn = sqlite3.connect('charts2.db')
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS chart (cid integer primary key autoincrement, date text, description text, name text,url text,fetch date)')
c.execute('CREATE TABLE IF NOT EXISTS track (track_id primary key not null, artist text, name text, buy text)')
c.execute('CREATE TABLE IF NOT EXISTS chart_pos (chart_id integer, track_id integer, position integer)')

jsonurl = urllib.urlopen(url)

rawChart = json.loads(jsonurl.read())


chartDate=rawChart['Date']
chartDescription=rawChart['Description']
chartName=rawChart['Name']
# chartID is null so ignored

#print 'Date: '+repr(chartDate)+' Descrtiption: '+repr(chartDescription )+ ' name: '+repr( chartName)+ ' url: '+url
c.execute('insert into charts (date,description,name,url,fetch) values(?,?,?,?,date(\'now\'))',(chartDate,chartDescription,chartName,url))
chartID=c.lastrowid
conn.commit()

for x in rawChart['Tracks']:
  artist= x[u'Artist']
  buy = x[u'Buy']
  name = x[u'Name']
  tid = x[u'id']
  position = x[u'Position']
 # print 'Artist: '+artist + ' Buy: '+repr(buy)+' name: '+ name+ ' id: ' +repr(tid) + ' position: ' +position
  
  c.execute('insert or ignore into track (track_id,artist,name, buy) values (?,?,?,?)',(tid, artist,name,buy))
  
  c.execute('insert into chart_pos (chart_id,track_id, position) values (?,?,?)', (chartID,tid,position))
  conn.commit()

c.close()
