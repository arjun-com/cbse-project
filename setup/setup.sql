create database schoolProjectDB;

create table users(
    uuid int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT;
    username varchar(100) NOT NULL,
    password varchar(64) NOT NULL,
    school varchar(100) NOT NULL,
    grade int(11) NOT NULL,
    section varchar(10),
    dob varchar(20),
    email varchar(100) NOT NULL,
    role varchar(50) NOT NULL
);

create table assignments(
    uaid int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT;
    subject varchar(50),
    startdate varchar(50),
    enddate varchar(50),
    grade int(11) NOT NULL,
    section varchar(10),
    school varchar(100) NOT NULL
);