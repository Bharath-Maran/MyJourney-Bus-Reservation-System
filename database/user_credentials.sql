CREATE TABLE USER_CREDENTIALS(
USER_ID INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
USERNAME VARCHAR(20) NOT NULL,
PASSWORD VARCHAR(20) NOT NULL,
USER_POWER VARCHAR (5) DEFAULT 'User' NOT NULL,
FIRST_NAME VARCHAR(20) NOT NULL,
LAST_NAME VARCHAR(20) NOT NULL,
DOB DATE NOT NULL,
GENDER VARCHAR(20) NOT NULL,
EMAIL VARCHAR(50) NOT NULL,
PHONE_NUMBER BIGINT NOT NULL,
WALLET INT DEFAULT 10000 NOT NULL,
USER_STATUS VARCHAR(20) DEFAULT 'Active' NOT NULL);

DROP TABLE USER_CREDENTIALS;
SELECT * FROM USER_CREDENTIALS;
USE BUS_DB;
SELECT * FROM BOOKING_DETAILS;	
DELETE FROM TRAVEL_DETAILS WHERE BUS_ID = 8;

ALTER TABLE USER_CREDENTIALS MODIFY WALLET INT DEFAULT 10000 NOT NULL;