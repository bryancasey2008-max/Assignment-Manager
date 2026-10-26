CREATE DATABASE IF NOT EXISTS assignment_db;
USE assignment_db;
 
CREATE TABLE IF NOT EXISTS assignments (
    assignment_id      INT AUTO_INCREMENT,
    title              VARCHAR(50)  NOT NULL,
    assignment_desc    VARCHAR(255) NOT NULL,
    assignment_subject VARCHAR(25)  NOT NULL,
    due_date           DATETIME     NOT NULL,
    complete           BOOLEAN      NOT NULL DEFAULT FALSE,
    created            TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (assignment_id)
);
 
