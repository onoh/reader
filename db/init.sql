create table blogs ( id integer primary key, url text, title text, unread integer, genre text);

create table entries ( id integer primary key, feed_id integer, url text, title text, date integer, content text, summary text, read integer);
