
var t;

var width = (window.innerWidth > 0) ? window.innerWidth -20 : screen.width -20;
var height = (window.innerHeight > 0) ? window.innerHeight : screen.height;

var loading = false;
var loader = { text: "LOADING", textVisible: true, theme: "a", textonly: false };

var type = null;

function delay( func, args, t ) { 
  setTimeout(function() {
    var f = new Function('return ('+func+')')();
    f.apply(null,args);
  },t);
}

function get_target ( target ) {
  if ( ! $(target).hasClass("entry") ) target = $(target).parents("div.entry");
  return target
}

function update_entry( target, cmd, toggle ) {

  if ( ! cmd ) return false;

  target = get_target( target );

  var id = target.attr("id").split("-")[1];
  var attr = false;

  if ( toggle && target.attr( cmd ) == "1" ) { attr = cmd; cmd = "un"+cmd; }
  else if ( target.attr( cmd ) == "0" ) attr = cmd;

  if ( attr ) {
    $.getJSON("./entry", { "id": id, "cmd": cmd, "json": null }, function(json) { target.attr( attr, json[attr] ); });
  }

}

function fetch_entries( id, cmd ) {

  if ( loading ) return false;

  if ( id ) id = id.split("-")[1];

  var params = { "id": id, "json": null, "mini": null };
  if ( cmd == "older" ) params.get = cmd;
  if ( type == "saved" ) params.saved = 1;
  else if ( type == "read" ) params.read = 1;

  loading = true;

  $.mobile.loading( "show", loader );

  $.getJSON("./", params, function(json) {

    if ( json.entries.length > 0 && cmd == "older" ) $("#entry-"+id).hide();
    for ( var i = 0 ; i < json.entries.length; i++ ) { add_entry( json.entries[i], cmd ); }

    $.mobile.loading( "hide" );

    loading = false;

  });
  
}

function swipe( command, target ) {

  $("body").attr("overflow","hidden");

  target = get_target( target );

  if ( command == "right" ) {
    var next = target.next("div.entry");
    update_entry( target, "read", false );
    if ( next.length ) { target.hide(); next.show(); } 
    else fetch_entries( target.attr("id"), "older");
  }
  else if ( command == "left" ) {
    var prev = target.prev("div.entry");
    if ( prev.length ) { target.hide(); prev.show(); }
//    else fetch_entries( target.attr("id"), "newer");
  }

}

function pad( val ) { return val > 10 ? val : "0"+val; }

function getDateTime( date ) {
  var dd = new Date( date*1000 );
  var date = pad(dd.getMonth()+1)+"/"+pad(dd.getDate())+" "+pad(dd.getHours())+":"+pad(dd.getMinutes());
  return date;
}

function setImageSize( target ) {
  if ( target.width > width ) {
    var ratio = width / target.width;
    $(target).width( target.width * ratio );
    $(target).height( target.height * ratio );
  }
}

function add_entry( entry, cmd ) {
  var div = $("<div>").addClass("entry").attr({ "id":"entry-"+entry.id, "data-role":"content", "saved": entry.saved, "read": entry.read });
  var date = getDateTime( entry.date );
  $("<div>").addClass("body")
    .append( $("<p>").addClass("info")
      .append( $("<span>").addClass("save").click(function(e){ update_entry( e.target, "saved", true)}) )
      .append( $("<span>").addClass("read").click(function(e){ update_entry( e.target, "read", true)}) ) 
      .append( $("<span>").addClass("feed").attr("feed",entry.feed_id) ) )
    .append( $("<p>").addClass("date").text( date ) )
    .append( $("<p>").addClass("title")
      .append( $("<a>").attr({"href":entry.url,"target": "_blank"}).text( entry.title ).click(function(e){ update_entry( e.target, "read", false) }) ) )
    .append( $("<div>").addClass("summary").html( entry.summary ) )
    .appendTo(div);

  div.find("*").removeAttr("style");
  div.find("img").each(function() { $(this).removeAttr("align"); setImageSize( this ); });
  div.find("img").load(function(e) { setImageSize( e.target ); });
  div.bind("swipeleft", function(e) { swipe( "left", e.target );   });
  div.bind("swiperight", function(e) { swipe( "right", e.target ); });

  if ( $("div.body:visible").length ) div.hide();

  if ( cmd == "newer" ) {
    div.prependTo("#entries");
  } else {
    div.appendTo("#entries");
  }

}

function init() {
  $("#entries").empty(); type = null; fetch_entries();
}


jQuery(function($){

  init();

  $("#header h1").click(function() { init(); });

  $("#saved").click(function() { $("#entries").empty(); type = "saved"; fetch_entries(); }); 

  $("#read").click(function() { $("#entries").empty(); type = "read"; fetch_entries(); });
  
});

