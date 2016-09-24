DROP TABLE IF EXISTS comment;
CREATE TABLE comment
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    body TEXT NOT NULL,
    user CHAR(100) NOT NULL,
    CONSTRAINT comment_user_email_fk FOREIGN KEY (user) REFERENCES user (email)
);
CREATE UNIQUE INDEX comment_id_uindex ON comment (id);

DROP TABLE IF EXISTS user;
CREATE TABLE user
(
    email CHAR(100) PRIMARY KEY NOT NULL,
    first_name CHAR(40) NOT NULL,
    last_name CHAR(40) NOT NULL,
    password CHAR(100) NOT NULL
);
CREATE UNIQUE INDEX user_email_uindex ON user (email);

DROP TABLE IF EXISTS account;
CREATE TABLE account
(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name CHAR(64) NOT NULL,
  balance REAL
);
CREATE UNIQUE INDEX account_id_uindex ON account (id);
