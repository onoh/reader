#!/usr/bin/python
# -*- encoding: utf-8 -*-
import json, sqlite3, re, time

class db(object):

  file = "./feed.sqlite3"

  def __init__( self ):
    self.con = sqlite3.connect( self.file )
    self.cur = self.con.cursor()


  def select( self, query, args=(), one=False ):
    self.cur.execute( query, args )
    res = self.cur.fetchall()
    return res

  def update( self, query,args=(), one=False ):
    self.cur.execute( query, args )

  def commit( self ):
    self.con.commit()


if __name__ == "__main__":
    f = open("./starred.json","r")
    data = json.loads(f.read())

    d = db()
    

    feeds = data["items"]
    for feed in feeds:
      blog = [ feed["origin"]["htmlUrl"] ]
      if blog[0] == "http://honwaka2ch.blog90.fc2.com/": blog[0] = "http://honwaka2ch.livedoor.biz/"
      title = feed["title"]
      entry_url = feed["alternate"][0]["href"]  
      id = d.select('select id from blogs where url = ?',[blog[0]])
      if not id:
        blog.append(feed["origin"]["title"])
        blog.append(feed["origin"]["streamId"][5:])
        d.update('insert into blogs values ( null, ?, ? , 0 , "Fanny News", ? )',blog)
        id = d.select('select id from blogs where url = ?',[blog[0]])
#      entry = [ id, url, title, date, summary, read, saved ]
      content = feed["content"]["content"] if feed.has_key("content") else feed["summary"]["content"]
      entry = [ id[0][0], feed["alternate"][0]["href"],feed["title"],feed["published"],content] 
      d.update('insert into entries values ( null, ?, ?, ?, ?, ?, 1, 1)',entry)
      
    d.commit()
    
    
