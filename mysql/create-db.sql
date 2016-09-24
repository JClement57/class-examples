DROP TABLE IF EXISTS user;

CREATE TABLE `user` (
  `username` varchar(40) NOT NULL,
  `password` varchar(45) NOT NULL,
  PRIMARY KEY (`username`)
);