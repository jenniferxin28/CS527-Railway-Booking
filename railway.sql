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
    schedule_id INT PRIMARY KEY AUTO_INCREMENT,
    transit_line_name VARCHAR(50),
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
    stop_id INT PRIMARY KEY AUTO_INCREMENT,
    schedule_id INT,
    sid INT,
    stop_order INT,
    stop_time_arrival DATETIME,
    stop_time_departure DATETIME,
    FOREIGN KEY (schedule_id) REFERENCES TrainSchedule(schedule_id) ON DELETE CASCADE;,
    FOREIGN KEY (sid) REFERENCES Station(sid)
);

CREATE TABLE Reservation (
    rid INT PRIMARY KEY AUTO_INCREMENT,
    date DATE,
    pid INT,
    total_fare FLOAT,
    schedule_id INT,
    dsid INT,
    asid INT,
    children INT DEFAULT 0,
    adults INT DEFAULT 0,
    seniors INT DEFAULT 0,
    disabled INT DEFAULT 0,
    FOREIGN KEY (pid) REFERENCES Customer(cid),
    FOREIGN KEY (schedule_id) REFERENCES TrainSchedule(schedule_id) ON DELETE CASCADE;,
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
       (4, 'Yellow Line'),
       (5, 'Gray Line');

INSERT INTO TrainSchedule (transit_line_name, tid, origin, dest, departure_time, arrival_time, travel_time, fare)
VALUES ('Blue Line', 1, 1, 5, '2024-12-24 08:00:00', '2024-12-24 08:45:00', '00:45:00', 2.75),
       ('Blue Line', 1, 1, 5, '2024-12-25 08:00:00', '2024-12-25 08:45:00', '00:45:00', 2.75),
       ('Red Line', 2, 2, 6, '2024-12-24 09:00:00', '2024-12-24 09:50:00', '00:50:00', 3.00),
       ('Green Line', 3, 3, 6, '2024-12-24 10:00:00', '2024-12-24 11:10:00', '01:10:00', 3.50),
       ('Yellow Line', 4, 4, 1, '2024-12-24 11:30:00', '2024-12-24 12:20:00', '00:50:00', 2.25),
       ('Gray Line', 5, 1, 6, '2024-12-01 07:00:00', '2024-12-01 08:30:00', '01:30:00', 4.50);


-- Blue Line (Schedule ID: 1)
INSERT INTO Stops (schedule_id, sid, stop_order, stop_time_arrival, stop_time_departure)
VALUES 
    (1, 1, 1, '2024-12-24 08:00:00', '2024-12-24 08:01:00'),
    (1, 3, 2, '2024-12-24 08:20:00', '2024-12-24 08:21:00'),
    (1, 5, 3, '2024-12-24 08:45:00', '2024-12-24 08:46:00');

-- Blue Line (Second Schedule, Schedule ID: 2)
INSERT INTO Stops (schedule_id, sid, stop_order, stop_time_arrival, stop_time_departure)
VALUES 
    (2, 1, 1, '2024-12-25 08:00:00', '2024-12-25 08:01:00'),
    (2, 3, 2, '2024-12-25 08:20:00', '2024-12-25 08:21:00'),
    (2, 5, 3, '2024-12-25 08:45:00', '2024-12-25 08:46:00');

-- Red Line (Schedule ID: 3)
INSERT INTO Stops (schedule_id, sid, stop_order, stop_time_arrival, stop_time_departure)
VALUES 
    (3, 2, 1, '2024-12-24 09:00:00', '2024-12-24 09:01:00'),
    (3, 4, 2, '2024-12-24 09:30:00', '2024-12-24 09:31:00'),
    (3, 6, 3, '2024-12-24 09:50:00', '2024-12-24 09:51:00');

-- Green Line (Schedule ID: 4)
INSERT INTO Stops (schedule_id, sid, stop_order, stop_time_arrival, stop_time_departure)
VALUES 
    (4, 3, 1, '2024-12-24 10:00:00', '2024-12-24 10:05:00'),
    (4, 5, 2, '2024-12-24 10:40:00', '2024-12-24 10:45:00'),
    (4, 6, 3, '2024-12-24 11:10:00', '2024-12-24 11:15:00');

-- Yellow Line (Schedule ID: 5)
INSERT INTO Stops (schedule_id, sid, stop_order, stop_time_arrival, stop_time_departure)
VALUES 
    (5, 4, 1, '2024-12-24 11:30:00', '2024-12-24 11:35:00'),
    (5, 2, 2, '2024-12-24 12:00:00', '2024-12-24 12:05:00'),
    (5, 1, 3, '2024-12-24 12:20:00', '2024-12-24 12:25:00');

-- Gray Line (Schedule ID: 6)
INSERT INTO Stops (schedule_id, sid, stop_order, stop_time_arrival, stop_time_departure)
VALUES 
    (6, 1, 1, '2024-12-01 07:00:00', '2024-12-01 07:05:00'),
    (6, 3, 2, '2024-12-01 07:45:00', '2024-12-01 07:50:00'),
    (6, 6, 3, '2024-12-01 08:30:00', '2024-12-01 08:35:00');


INSERT INTO Reservation (rid, date, pid, total_fare, schedule_id, dsid, asid, children, adults, seniors, disabled)
VALUES 
    (1, '2024-12-24', 1, 2.75, 1, 1, 5, 0, 1, 0, 0),
    (2, '2024-12-24', 2, 3.00, 3, 2, 6, 0, 1, 0, 0),
    (3, '2024-12-01', 1, 9.00, 6, 1, 6, 0, 1, 0, 0);
    
CREATE TABLE faqs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question VARCHAR(255) NOT NULL,
    answer TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO faqs (question, answer)
VALUES 
('What is the meaning of life?', '42'),
('Do you offer international shipping?', NULL);



