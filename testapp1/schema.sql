drop table if exists users;
create table users (
  id integer primary key autoincrement,
  user_name text not null,
  password text not null
);