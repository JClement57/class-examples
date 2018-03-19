DROP TABLE IF EXISTS comment;
DROP TABLE IF EXISTS member;
DROP TABLE IF EXISTS account;

CREATE TABLE member
(
  email      VARCHAR(100) NOT NULL
    CONSTRAINT user_pkey
    PRIMARY KEY,
  first_name VARCHAR(40)  NOT NULL,
  last_name  VARCHAR(40)  NOT NULL,
  password   VARCHAR(25)  NOT NULL
);
CREATE UNIQUE INDEX user_email_uindex
  ON member (email);
COMMENT ON TABLE member IS 'System user';

CREATE TABLE comment
(
  id     SERIAL       NOT NULL
    CONSTRAINT comment_pkey
    PRIMARY KEY,
  body   TEXT         NOT NULL,
  member VARCHAR(100) NOT NULL
    CONSTRAINT member_email_fk
    REFERENCES member (email)
);
CREATE UNIQUE INDEX comment_id_uindex
  ON comment (id);
COMMENT ON TABLE comment IS 'Comments from a user';

CREATE TABLE account
(
  id      SERIAL      NOT NULL
    CONSTRAINT account_pkey
    PRIMARY KEY,
  name    VARCHAR(64) NOT NULL,
  balance REAL        NOT NULL
);
CREATE UNIQUE INDEX account_id_uindex
  ON account (id);
