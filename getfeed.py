#!/data/virt/flask/bin/python
# -*- encoding: utf-8 -*-

import feedparser, sqlite3
import time, re


class db(object):

  file = "./db/feed.sqlite3"

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

    d = db()

    for feeddb in d.select('select id,feed_url from blogs where get = 1'):

      id = feeddb[0]
      url = feeddb[1]

      fp = feedparser.parse(url)

      if fp:
        for entry in fp.entries:

          if entry.has_key("published_parsed"): date = time.mktime(entry.published_parsed) + 32400
          else: date = time.mktime(entry.updated_parsed) + 32400

          if entry.has_key("content"): summary = entry.content[0].value
          else: summary = entry.summary

          article = [ id, entry.link, entry.title, date, summary ]

          target = d.select('select id from entries where url = ?',[ entry.link ])
          if not target and not re.search("^PR|AD",entry.title):
            d.update('insert into entries values(null,?,?,?,?,?,0,0)',article)

          unread = d.select('select count(read) from entries where feed_id=? and read != 1',[ id ])[0][0]
          d.update('update blogs set unread = ? where id = ?',[ unread, id ] )
 
    d.commit()
