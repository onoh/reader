#!../virt/flask/bin/python

from flask import Flask, render_template, request, json, make_response, g, redirect, url_for
import sqlite3, time, re, feedparser

app = Flask(__name__)
app.cookie = []
#app.db = "./db/feed.sqlite3"


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class db(object):

  def __init__( self, file ):
    self.con = sqlite3.connect( file )
    self.con.row_factory = dict_factory
    self.cur = self.con.cursor()

  def select( self, query, args=(), one=False ):
    self.cur.execute( query, args )
    return self.cur.fetchall()

  def genres( self ):
    res = { "genres": self.select( "select distinct(genre) as label from blogs" ) }
    for target in res["genres"]:
      target["unread"] = 0
      target["blogs"] =  self.select( 'select * from blogs where genre = ?', [ target["label"] ] )
      for blog in target["blogs"]:
        target["unread"] = target["unread"] + blog["unread"]
    
    res.update( self.select('select count(id) as saved from entries where saved = 1')[0] )
    return res

  def entries( self  ):
    res = { "entries": "" }
    read = " read = %(read)s and"%app.params if app.params["saved"] == 0 else " read in (0,1) and "
    search = app.search + read + " saved = %(saved)s order by id %(sort)s limit %(limit)s" % app.params
    if app.params["get"] == "older":
      search = "id < %d and"%( app.params["id"] ) + read + " saved = %(saved)s order by id desc limit %(limit)s" % app.params
#    search = app.search + read + " saved = %(saved)s order by date %(sort)s limit %(limit)s offset %(offset)s" % app.params
    if app.params["search"]: search = "title like '%%%(search)s%%' order by date %(sort)s limit %(limit)s" % app.params
#    if app.params["search"]: search = "title like '%%%(search)s%%' order by date %(sort)s limit %(limit)s offset %(offset)s" % app.params
#    search = app.search + " read = %(read)s and saved = %(saved)s order by date %(sort)s limit %(limit)s offset %(offset)s" % app.params
    res["entries"] = self.select( 'select * from entries where %s' % search )

    return res

  def entry( self, id ):
    return self.select("select * from entries where id = ?",[id])

  def entry_status( self, id ):
    return self.select('select id, read, saved, feed_id, url from entries where id = ?',[id])

  def update( self, query, args=(), one=False ):
    try: 
      ret = self.cur.execute( query, args )
      self.commit()
    except sqlite3.OperationalError: pass

  def update_entry( self, id, cmd ):
    self.update( 'update entries set %(cmd)s where id = %(id)s' % { "id": id, "cmd": cmd } )
    res = self.entry_status( id )
    if len(res) > 0: 
      self.update_unread( res[0]["feed_id"] )
      return res[0]
    return { "error": True }

  def update_entries( self, lists ):
    for data in lists:
      if len(data[0].split("_")) == 2:
        cmds = { "open": "read = 1", "read": "read = 1", "unread": "read = 0", "saved": "saved = 1", "unsaved": "saved = 0" }
        [ cmd, id ] = data[0].split("_")
        if cmd in cmds.keys(): update = cmds.items()[cmds.keys().index(cmd)][1]
        if update: app.db.update_entry( id, update)

  def update_unread( self, feed_id ):
    unread = self.select('select count(read) as unread from entries where feed_id=? and read != 1', [ feed_id ])[0]["unread"]
    self.update('update blogs set unread = ? where id = ?', [ unread, feed_id ] )

  def commit( self ):
    self.con.commit()


@app.before_request
def before_request():

    app.db = db("./db/feed.sqlite3")

    limit = request.args.get( "limit", default=20, type=int )
#    offset = request.args.get( "offset", default=0, type=int )
    read = request.args.get( "read", default=0, type=int )
    saved = request.args.get( "saved", default=0, type=int )
    id = request.args.get( "id", default=0, type=int )
    cmd = request.args.get( "cmd", default="", type=str )
    get = request.args.get( "get", default="", type=str )
    genre = request.args.get( "genre", default="", type=str )
    q = request.args.get( "q", default="", type=unicode )

    if request.args.get("sort") in [ "older", "asc"]: sort = "asc"
    else: sort = "desc"

#    offset = request.form.get( "offset", default=0, type=int )
#    if request.form.has_key("next"): offset = offset + limit
#    if request.form.has_key("prev") and offset >= limit: offset = offset - limit

    app.params = { "genre": genre, "cmd": cmd, "id": id, "limit": limit, "saved": saved, "sort": sort, "read": read, "search": q, "get": get }
#    app.params = { "genre": genre, "cmd": cmd, "id": id, "limit": limit, "offset": offset, "saved": saved, "sort": sort, "read": read, "search": q }

    app.search = ""

#    if get == "newer":
#      app.search = "id > %d and"%( app.params["id"] )

    app.jsonify = True if request.args.has_key("json") else False
    app.mini = True if request.args.has_key("mini") else False

    if request.form: app.db.update_entries( request.form.items() )


@app.route("/", methods=['GET', 'POST'])
def home():

    res = { "title": "All", "query": "?" }
    if not app.mini: res.update( app.db.genres() )
          
#    if app.params["saved"] == 1: res.update( { "title": "Saved", "query": "?saved=1&" } )

    res.update( app.db.entries() )

    return response(res)


@app.route("/swipe")
def swipe():

    res = { "title": "All", "query": "?" }
    res.update( app.db.genres() )

#    if app.params["saved"] == 1: res.update( { "title": "Saved", "query": "?saved=1&" } )

    res.update( app.db.entries() )

    res.update( { "params": app.params } )
    return render_template( "mobile.html", res=res, time=time )
#    return response(res)




@app.route("/blog", methods=['GET', 'POST'])
def blog():

    res = app.db.genres()

    if ( app.params["id"] ):
      blogs = reduce(list.__add__, [ x for x in [ target["blogs"] for target in res["genres"] ] ],[])
      if app.params["id"] in [ x["id"] for x in blogs ]:
        blog = blogs[[ x["id"] for x in blogs ].index(app.params["id"])]
        app.search = "feed_id = %d and"%( app.params["id"] )
        res.update( { "title": blog["title"], "query": "./blog?id=%d&"%(app.params["id"]) } )
        res.update( app.db.entries() )

    return response(res)


@app.route("/genre", methods=['GET', 'POST'])
def genre():

    res = app.db.genres()

    if app.params["genre"] in [ target["label"] for target in res["genres"] ]:
      res.update( { "title": app.params["genre"], "genre": app.params["genre"] } )
      blogs = res["genres"][[ target["label"] for target in res["genres"] ].index(app.params["genre"])]["blogs"]
      ids = [ blog["id"] for blog in blogs ]
      app.search = "feed_id in ({0}) and".format(', '.join('%s' for _ in ids))%tuple(ids)
      res.update( { "query": "./genre?genre=%s&"%(app.params["genre"]) } )
      res.update( app.db.entries() )
      
    return response( res )


@app.route("/entry")
def entry():

    res = { "error": True }

    if ( app.params["id"] and app.params["cmd"] ):

      update = ""
      cmds = { "open": "read = 1", "read": "read = 1", "unread": "read = 0", "saved": "saved = 1", "unsaved": "saved = 0" }
      if app.params["cmd"] in cmds.keys(): update = cmds.items()[cmds.keys().index(app.params["cmd"])][1]

      if update: res = app.db.update_entry( app.params["id"], update)

      if app.params["cmd"] == "open": return redirect( res["url"] )

      if not app.jsonify: return redirect( url_for("home") )
        
    return response( res )


@app.route("/settings")
def settings():

    res = { "error" : True, }

    '''
    if request.args.has_key("add") :
      feed_url = request.args.get("add")
      fp = feedparser.parse( feed_url )
      if fp and not request.args.has_key("title") :
        return json.dumps(fp.feed)
      elif fp :
        f = fp.feed
        genre = request.args.get("genre")
        if not genre: genre = "Default"
        title = request.args.get("title")
        if not title: title = f.title
        feed = { "url": f.link, "title": title, "genre": genre, "feed_url": feed_url }
        target = select('select id from blogs where url = ?',[feed["url"]])
        if not target: 
          update('insert into blogs values(null,"%(url)s","%(title)s",0,"%(genre)s","%(feed_url)s",1)'%feed)
          return json.dumps({"result":"ok"})
        return json.dumps({"result":"error"})
    '''

    res.update( app.db.genres() )

    return render_template("settings.html",res=res)


@app.route("/mini")
def mini():
    res = { "error": True, "entry": "", "list": [], "offset": app.offset }
    id = request.args.get("id")

    condition = 'read = ' + app.read

    cmd = request.args.get("list")

    if cmd or app.search:
      res["query"] = "list="+cmd if cmd else "q="+app.search
      if cmd == "saved": condition = 'saved = 1'
      elif app.search: condition = "entries.title like '%"+app.search+"%'"
      res["list"] = select('select entries.feed_id,entries.id,entries.title,entries.url,datetime(entries.date,"unixepoch","localtime"),entries.summary,entries.read,entries.saved,blogs.title from entries inner join blogs on entries.feed_id = blogs.id where %(condition)s order by date %(order)s limit 40 offset %(offset)s'% { "condition":condition, "order":app.order, "offset":app.offset } )

    else :

      saved = request.args.get("saved")
      if saved:
        s = select('select saved from entries where id = ?',[ saved ])[0]
        if s:
          set_value = 'saved = 1' if s[0] == 0 else 'saved = 0'
          update('update entries set %(set_value)s where id = ?'%{"set_value":set_value},[saved])
          condition = 'entries.id = ' + saved

      res["entry"] = select('select entries.feed_id,entries.id,entries.title,entries.url,datetime(entries.date,"unixepoch","localtime"),entries.summary,entries.read,entries.saved,blogs.title from entries inner join blogs on entries.feed_id = blogs.id where %(condition)s order by date %(order)s limit 1 offset %(offset)s'% { "condition":condition, "order":app.order, "offset":app.offset } )[0]
#      update('update entries set read = 1 where id = ?',[res["entry"][1]])

    return render_template("mini.html",res=res,len=len)


def response( res ):

    if app.jsonify:
      obj = make_response( json.dumps( res ) )
      obj.mimetype='application/json'
    else:
      res.update( { "params": app.params } )
      if ( "Android" in request.headers.get("User-Agent") ): obj = render_template( "mobile.html", res=res, time=time )
      else: obj = render_template( "index.html", res=res, time=time )
#      obj = render_template( "debug.html", res=res )

    return obj
#    return render_template( "index.html", res=res, time=time )



@app.route("/refresh")
def refresh():

    print "refresh"
    for feed in select('select id,feed_url from blogs'):
      feed_id = feed[0]
      unread = select('select count(read) from entries where feed_id=? and read != 1',[ feed_id ])[0][0]
      update('update blogs set unread = ? where id = ?',[ unread, feed_id ] )

def refresh_unread( feed_id ):
    unread = select('select count(read) from entries where feed_id=? and read != 1',[ feed_id ])[0][0]
    update('update blogs set unread = ? where id = ?',[ unread, feed_id ] )


def select( query, args=(), one=False ):
    cur = app.con.cursor()
    cur.execute( query, args )
    res = cur.fetchall()
    return res

def update( query,args=(), one=False ):
    cur = app.con.cursor()
    try: cur.execute( query, args )
    except sqlite3.OperationalError: pass


if __name__ == "__main__" :
    app.debug = True
    app.run(host="127.0.0.1",port=5111)
