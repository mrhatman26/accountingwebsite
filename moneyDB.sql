DROP DATABASE IF EXISTS moneydatabase;
CREATE DATABASE moneydatabase;
USE moneydatabase;

DROP TABLE IF EXISTS table_users;
CREATE TABLE table_users(
    user_id INT NOT NULL AUTO_INCREMENT,
    user_name TEXT  NOT NULL,
    user_pass TEXT NOT NULL,
    user_isAdmin BOOLEAN DEFAULT 0
    PRIMARY KEY(user_id)
);