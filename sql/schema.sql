PRAGMA foreign_keys = ON;

CREATE TABLE users(
  username VARCHAR(20) NOT NULL,
  fullname VARCHAR(40) NOT NULL,
  email VARCHAR(40) NOT NULL,
  filename VARCHAR(64) NOT NULL,
  password VARCHAR(256) NOT NULL,
  created DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(username)
);

CREATE TABLE posts(
  postid INTEGER,
  filename VARCHAR(64) NOT NULL,
  created DATETIME DEFAULT CURRENT_TIMESTAMP,
  owner VARCHAR(20) NOT NULL,
  PRIMARY KEY(postid),
  foreign key (owner) references users(username) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE following( -- username1 follows username2
  username1 VARCHAR(20),
  username2 VARCHAR(20),
  created DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(username1, username2),
  foreign key (username1) references users(username) ON UPDATE CASCADE ON DELETE CASCADE,
  foreign key (username2) references users(username) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE comments(
  commentid INTEGER,
  owner VARCHAR(20),
  postid INTEGER,
  text VARCHAR(1024),
  created DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(commentid),
  foreign key (owner) references users(username) ON UPDATE CASCADE ON DELETE CASCADE,
  foreign key (postid) references posts(postid) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE likes(
  owner VARCHAR(20),
  postid INTEGER,
  created DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(owner, postid),
  foreign key (owner) references users(username) ON UPDATE CASCADE ON DELETE CASCADE,
  foreign key (postid) references posts(postid) ON UPDATE CASCADE ON DELETE CASCADE
)
