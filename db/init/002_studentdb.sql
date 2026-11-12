-- Mo rong 3: CSDL studentdb + bang students (>= 3 ban ghi)
CREATE DATABASE IF NOT EXISTS studentdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE studentdb;

CREATE TABLE IF NOT EXISTS students(
  id INT PRIMARY KEY AUTO_INCREMENT,
  student_id VARCHAR(10),
  fullname VARCHAR(100),
  dob DATE,
  major VARCHAR(50)
);

INSERT INTO students(student_id, fullname, dob, major) VALUES
  ('SV001', 'Nguyen Van A', '2002-03-15', 'Computer Science'),
  ('SV002', 'Tran Thi B',   '2001-11-02', 'Data Science'),
  ('SV003', 'Le Van C',     '2002-07-20', 'Cybersecurity');

-- User rieng cho Application Server (nguyen tac least privilege)
CREATE USER IF NOT EXISTS 'appuser'@'%' IDENTIFIED BY 'apppass';
GRANT SELECT, INSERT, UPDATE, DELETE ON studentdb.* TO 'appuser'@'%';
GRANT SELECT ON minicloud.* TO 'appuser'@'%';
FLUSH PRIVILEGES;
