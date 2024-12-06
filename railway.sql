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
	
# Customer table
CREATE TABLE Customer (
    cid INT PRIMARY KEY AUTO_INCREMENT,
    last_name VARCHAR(30),
    first_name VARCHAR(30),
    email VARCHAR(50),
    username VARCHAR(30),
    password VARCHAR(30)
);

INSERT INTO Customer (last_name, first_name, email, username, password)
VALUES ('Stark', 'Tony', 'customer1@gmail.com', 'customer1', 'pass'),
       ('Rogers', 'Steve', 'customer2@gmail.com', 'customer2', 'pass');

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
    travel_time TIME,
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
    rid INT PRIMARY KEY AUTO_INCREMENT,
    date DATE,
    pid INT,
    total_fare FLOAT,
    tid INT,
    dsid INT,
    asid INT,
    transit_line_name VARCHAR(50),
    children INT DEFAULT 0,
    adults INT DEFAULT 0,
    seniors INT DEFAULT 0,
    disabled INT DEFAULT 0,
    FOREIGN KEY (pid) REFERENCES Customer(cid),
    FOREIGN KEY (tid) REFERENCES Train(tid),
    FOREIGN KEY (transit_line_name) REFERENCES TrainSchedule(transit_line_name),
    FOREIGN KEY (dsid) REFERENCES Station(sid),
    FOREIGN KEY (asid) REFERENCES Station(sid)
);

# Data inserts
INSERT INTO Station (sid, name, city, state)
VALUES (1, 'Times Square', 'New York', 'NY'),
       (2, 'Grand Central', 'New York', 'NY'),
       (3, 'Union Square', 'New York', 'NY'),
       (4, 'Wall Street', 'New York', 'NY'),
       (5, 'Fulton Street', 'New York', 'NY'),
       (6, 'Brooklyn Bridge', 'New York', 'NY');

INSERT INTO Train (tid, transit_line_name)
VALUES (1, 'Blue Line'),
       (2, 'Red Line'),
       (3, 'Green Line'),
       (4, 'Yellow Line');

INSERT INTO TrainSchedule (transit_line_name, tid, origin, dest, departure_time, arrival_time, travel_time, fare)
VALUES ('Blue Line', 1, 1, 5, '2024-12-24 08:00:00', '2024-12-24 08:45:00', '00:45:00', 2.75),
       ('Red Line', 2, 2, 6, '2024-12-24 09:00:00', '2024-12-24 09:50:00', '00:50:00', 3.00),
       ('Green Line', 3, 3, 6, '2024-12-24 10:00:00', '2024-12-24 11:10:00', '01:10:00', 3.50),
	   ('Yellow Line', 4, 4, 1, '2024-12-24 11:30:00', '2024-12-24 12:20:00', '00:50:00', 2.25);

INSERT INTO Stops (stop_id, transit_line_name, sid, stop_order, stop_time_arrival, stop_time_departure)
VALUES (1, 'Blue Line', 1, 1, '2024-12-24 08:00:00', '2024-12-24 08:01:00'),
       (2, 'Blue Line', 3, 2, '2024-12-24 08:20:00', '2024-12-24 08:21:00'),
       (3, 'Blue Line', 5, 3, '2024-12-24 08:45:00', '2024-12-24 08:46:00'),
       (4, 'Red Line', 2, 1, '2024-12-24 09:00:00', '2024-12-24 09:01:00'),
       (5, 'Red Line', 4, 2, '2024-12-24 09:30:00', '2024-12-24 09:31:00'),
       (6, 'Red Line', 6, 3, '2024-12-24 09:50:00', '2024-12-24 09:51:00'),
       (7, 'Green Line', 3, 1, '2024-12-24 10:00:00', '2024-12-24 10:05:00'),
	   (8, 'Green Line', 5, 2, '2024-12-24 10:40:00', '2024-12-24 10:45:00'),
	   (9, 'Green Line', 6, 3, '2024-12-24 11:10:00', '2024-12-24 11:15:00'),
       (10, 'Yellow Line', 4, 1, '2024-12-24 11:30:00', '2024-12-24 11:35:00'),
       (11, 'Yellow Line', 2, 2, '2024-12-24 12:00:00', '2024-12-24 12:05:00'),
       (12, 'Yellow Line', 1, 3, '2024-12-24 12:20:00', '2024-12-24 12:25:00');

-- Past Train schedule insert
INSERT INTO Train (tid, transit_line_name)
VALUES (5, 'Gray Line');
INSERT INTO TrainSchedule (transit_line_name, tid, origin, dest, departure_time, arrival_time, travel_time, fare)
VALUES ('Gray Line', 5, 1, 6, '2024-12-01 07:00:00', '2024-12-01 08:30:00', '01:30:00', 4.50);
INSERT INTO Stops (stop_id, transit_line_name, sid, stop_order, stop_time_arrival, stop_time_departure)
VALUES (13, 'Gray Line', 1, 1, '2024-12-01 07:00:00', '2024-12-01 07:05:00'),
       (14, 'Gray Line', 3, 2, '2024-12-01 07:45:00', '2024-12-01 07:50:00'),
       (15, 'Gray Line', 6, 3, '2024-12-01 08:30:00', '2024-12-01 08:35:00');
INSERT INTO Reservation (rid, date, pid, total_fare, tid, dsid, asid, transit_line_name, children, adults, seniors, disabled)
VALUES (3, '2024-12-01', 1, 9.00, 5, 1, 6, 'Gray Line', 0, 1, 0, 0);

