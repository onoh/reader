
var isLoading = false;
var body_height;

var s;

function get_entry( id, cmd ) {
  $.getJSON("./entry?id="+id+"&cmd="+cmd+"&json",function(json) {
    if ( ! json.error ) {
      target = $("#entry"+json.id);
      if ( json.read == 0 ) target.find("input.read").prop("checked",false);
      else target.find("input.read").prop("checked",true);
      if ( json.saved == 0 ) target.find("input.save").prop("checked",false);
      else target.find("input.save").prop("checked",true);
      update_count( json.feed_id, cmd );
    } else console.log("error on get_entry",json)
  });
}

function update_count( feed_id, cmd ) {
  var target = $("li[i="+feed_id+"]");
  var num = parseInt(target.find("span.unread").text());
  if ( cmd == "read" )  num--; 
  else if ( cmd == "unread" ) num++;
  if ( num >= 0  ) target.find("span.unread").text(num);
}

function loading() {
  isLoading = true;
  var offset = parseInt($("#offset").text()) + 40;
  $("#offset").text(offset);
  var div = $("<div>").addClass("loading").text(" Loading...");
  $("<img>").attr("src","./static/loading.gif").prependTo(div);
  div.appendTo("#body");

  if ( location.search ) query = location.search + "&offset="+offset;
  else query = "?offset="+offset;

  $.getJSON(location.pathname+query+"&json",function(json) {
    for ( var i = 0 ; i < json.length; i++) {
      body_height += 26;
      $("<p>").attr("id","entry"+json[i][1])
       .append( $("<span>").addClass("save"+json[i][7]).click(function(){click_entry($(this));}) )
       .append( $("<span>").addClass("read"+json[i][6]).click(function(){click_entry($(this));}) )
       .append( $("<span>").addClass("feed feed"+json[i][0]).attr("feed","feed"+json[i][0]) )
       .append( $("<span>").addClass("date").text(json[i][4].substr(5,11).replace("-",".")) )
       .append( $("<span>").addClass("title").text(json[i][2]).click(function(){click_entry($(this));}) )
       .appendTo("#body");

      var div = $("<div>").addClass("summary").html(json[i][5]);
      $("<h3>").addClass("title")
       .append( $("<a>").attr({"href":json[i][3],"target":"_blank"}).text(json[i][2])
         .append( $("<img>").attr("src","./static/icon-exlink.png") ) )
       .prependTo(div);
      $("<br>").addClass("clear").appendTo(div);
      div.appendTo("#body");
    }
    $("#body .loading").remove();
    isLoading = false;
  });


//  console.log(location.pathname+query);
}

function entry_click( target, cmd ) {
  var parent = target.parents(".entry");
  var id = parent.attr("id").substr("5");
  var feed_id = parent.children("a.feed").attr("feed");
  
  if ( ! cmd ) {
    if ( target.hasClass("save") )  cmd = target.is(":checked") ? "save": "unsave";
    else if ( target.hasClass("read") )  cmd = target.is(":checked") ? "read": "unread";
  }

  if ( cmd ) get_entry( id, cmd );
 
//  if ( target.is(":checked") ) {
//    if ( target.hasClass("save") )  cmd = parent.hasClass("save0") ? "save": "unsave";
//  console.log( target.is(":checked") );
//  console.log( target.prev().val() );
/*
  if ( ! cmd ) {
    if ( target.hasClass("save") )  cmd = parent.hasClass("save0") ? "save": "unsave";
    else if ( target.hasClass("read") ) cmd = parent.hasClass("read0") ? "read": "unread";
    else if ( target.hasClass("feed") ) location.href = "./blog?id="+target.attr("feed");
  }
  if ( cmd ) get_entry( id, cmd );
*/
//  return false;
}

function entry_open( target ) {
  var url = $(target).attr("href");
  window.open(url);
  entry_click(target, "read");
}

jQuery(function($) {

  body_height = $("#body").height();

  $("div.body").each(function() { $(this).find("img:first").show(); }).click(function() { entry_open($(this))});

  $("div.body a").removeAttr("href")
//  $("div.entry > p.info > label").click(function() { entry_click($(this)); });
  $("div.entry > p.info > input").change(function() { entry_click($(this)); });

  $("form#refresh").submit(function() { location.refresh(); return false; });

/*
  $("#genres a.genre").each(function() {
    var num = 0;
    $(this).next("ul").find("li span").each(function() {
      num += parseInt($(this).text());
    });
    $(this).children("span").text(num);
  });
*/

/*

  $("#add").submit(function() {
    var feed = $("#add input.url").val();
    var title = $("#add input.title").val();
    var genre = $("#add input.genre").val();
    if ( ! title && ! genre ) {
      $.getJSON("./settings",{"add":feed},function(json) {
        $("#add input.title").val(json.title);
      });
    } else {
      $.getJSON("./settings",{"add":feed,"title":title,"genre":genre},function(json) {
        if ( json.result == "ok" ) location.reload();
        else alert("error!!");
      });
    }
    return false;
  });
*/

/*
  $("#body").scroll(function() {
    var scroll = $("#body").scrollTop();
    if ( body_height - scroll < 40 && ! isLoading ) loading();
//    $("span.height").text(body_height);
  });
*/

});
