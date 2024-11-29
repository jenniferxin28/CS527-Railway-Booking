# database creation
DROP DATABASE IF EXISTS railway;
CREATE DATABASE railway;
USE railway;

# table creations
CREATE TABLE Employee (
    SSN INT PRIMARY KEY,
    last_name VARCHAR(30),
    first_name VARCHAR(30),
    username VARCHAR(30),
    password VARCHAR(30),
    level ENUM('rep', 'admin')
);

# Employee sample data
INSERT INTO Employee (SSN, last_name, first_name, username, password, level)
VALUES (1, 'Doe', 'John', 'admin', 'pass', 'admin'),
(2, 'Doe', 'Jane', 'rep', 'pass', 'rep');


CREATE TABLE Customer (
    cid INT PRIMARY KEY AUTO_INCREMENT,
    last_name VARCHAR(30),
    first_name VARCHAR(30),
    email VARCHAR(50),
    username VARCHAR(30),
    password VARCHAR(30),
    discount ENUM('children', 'adult', 'senior', 'disabled')
);

# Customer sample data
INSERT INTO Customer (last_name, first_name, email, username, password, discount)
VALUES ('Roe', 'Richard', 'customer1@gmail.com', 'adult_customer', 'pass', 'adult'),
('Kid', 'Kid', 'customer2@gmail.com', 'kid_customer', 'pass', 'children');

CREATE TABLE Station (
    sid INT PRIMARY KEY,
    name VARCHAR(30),
    city VARCHAR(30),
    state VARCHAR(30)
);

CREATE TABLE Train (
    tid INT PRIMARY KEY,
    transit_line_name VARCHAR(50)  
);

CREATE TABLE TrainSchedule (
    transit_line_name VARCHAR(50) PRIMARY KEY,
    tid INT,
    origin INT,
    dest INT,
    departure_time DATETIME,
    arrival_time DATETIME,
    travel_time DATETIME,
    fare FLOAT,
    FOREIGN KEY (tid) REFERENCES Train(tid),
    FOREIGN KEY (origin) REFERENCES Station(sid),
    FOREIGN KEY (dest) REFERENCES Station(sid)
);


CREATE TABLE Stops (
    stop_id INT PRIMARY KEY,
    transit_line_name VARCHAR(50),
    sid INT,
    stop_order INT,
    stop_time_arrival DATETIME,
    stop_time_departure DATETIME,
    FOREIGN KEY (transit_line_name) REFERENCES TrainSchedule(transit_line_name),
    FOREIGN KEY (sid) REFERENCES Station(sid)
);


CREATE TABLE Reservation (
    rid INT PRIMARY KEY,
    date DATE,
    pid INT,
    total_fare FLOAT,
    tid INT,
    dsid INT,
    asid INT,
    transit_line_name VARCHAR(50),
    FOREIGN KEY (pid) REFERENCES Customer(cid),
    FOREIGN KEY (tid) REFERENCES Train(tid),
    FOREIGN KEY (transit_line_name) REFERENCES TrainSchedule(transit_line_name),
    FOREIGN KEY (dsid) REFERENCES Station(sid),
    FOREIGN KEY (asid) REFERENCES Station(sid)
);
