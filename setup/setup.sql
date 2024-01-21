create user IF NOT EXISTS "school-admin"@"localhost" identified with mysql_native_password by "password";
grant all privileges on schoolProjectDB.* to "school-admin"@"localhost";

create database IF NOT EXISTS schoolProjectDB;

create table IF NOT EXISTS users(
    uuid int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
    username varchar(100) NOT NULL,
    password varchar(64) NOT NULL,
    school varchar(100) NOT NULL,
    grade int(11) NOT NULL,
    section varchar(10),
    dob varchar(20),
    email varchar(100) NOT NULL,
    role varchar(50) NOT NULL,
	teaching_classes varchar(100) NOT NULL
);

create table IF NOT EXISTS assignments(
    uaid int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
    subject varchar(50),
    startdate varchar(50),
    enddate varchar(50),
    grade int(11) NOT NULL,
    section varchar(10),
    school varchar(100) NOT NULL
);


create table IF NOT EXISTS tests(
    utid int NOT NULL auto_increment PRIMARY KEY,
    subject varchar(50) NOT NULL,
    school varchar(100) NOT NULL,
    startdate varchar(50) NOT NULL,
    enddate varchar(50) NOT NULL,
    starttime varchar(50) NOT NULL,
    endtime varchar(50) NOT NULL,
    testduration int NOT NULL,
    class varchar(20) NOT NULL,
    assigner_uuid int NOT NULL,
    question_json text NOT NULL
);

create table IF NOT EXISTS test_scores(
    utsid int NOT NULL PRIMARY KEY AUTO_INCREMENT,
    uuid int NOT NULL,
    utid int NOT NULL,
    score int NOT NULL
)