create database IF NOT EXISTS schoolProjectDBTEST2;

create user IF NOT EXISTS "school-admin"@"localhost" identified by "password";
grant all privileges on schoolProjectDBTEST2.* to "school-admin"@"localhost";

use schoolProjectDBTEST2;

create table IF NOT EXISTS users(
    uuid int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
    username varchar(100) NOT NULL,
    password varchar(64) NOT NULL,
    school varchar(100) NOT NULL,
    grade int(11) NOT NULL,
    section char(2) NOT NULL,
    dob date,
    email varchar(255) NOT NULL unique,
    role ENUM("student", "teacher", "admin") NOT NULL,
    CHECK(grade >= -2 and grade <= 12)
);

create table IF NOT EXISTS teacher_classes(
    utcid int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
    grade int(11) NOT NULL,
    section char(2) NOT NULL,
    position varchar(50) NOT NULL,
    uuid int(11) NOT NULL,
    CHECK(grade >= -2 and grade <= 12),
    FOREIGN KEY(uuid) REFERENCES users(uuid)
);

create table IF NOT EXISTS assignments(
    uaid int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
    subject varchar(50),
    startdatetime date default current_date() NOT NULL,
    enddatetime date default current_date() NOT NULL,
    grade int(11) NOT NULL,
    section char(2) NOT NULL,
    school varchar(100) NOT NULL
);

create table IF NOT EXISTS tests(
    utid int NOT NULL auto_increment PRIMARY KEY,
    subject varchar(50) NOT NULL,
    school varchar(100) NOT NULL,
    startdatetime datetime default current_timestamp NOT NULL,
    enddatetime datetime default current_timestamp NOT NULL,
    testduration int NOT NULL,
    grade int NOT NULL,
    section int NOT NULL,
    assigner_uuid int NOT NULL,
    question_json text NOT NULL,
    CHECK(grade >= -2 and grade <= 12),
    FOREIGN KEY(assigner_uuid) REFERENCES users(uuid)
);

create table IF NOT EXISTS test_scores(
    utsid int NOT NULL PRIMARY KEY AUTO_INCREMENT,
    uuid int NOT NULL,
    utid int NOT NULL,
    score int NOT NULL,
    max_score int NOT NULL,
    FOREIGN KEY(uuid) REFERENCES users(uuid),
    FOREIGN KEY(utid) REFERENCES tests(utid)
)
