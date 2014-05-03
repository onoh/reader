#!/usr/bin/python
# -*- encoding: utf-8 -*-
import json, sqlite3, re, time

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
    f = open("db/starred.json","r")
    data = json.loads(f.read())

    d = db()
    
    for key in data["items"][0]: print key



