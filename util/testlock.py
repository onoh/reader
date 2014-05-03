#!../virt/flask/bin/python
# -*- encoding: utf-8 -*-

import time, re,  sqlite3

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
    while True:
      d.update('update blogs set unread = 1600 where id = 1' )

