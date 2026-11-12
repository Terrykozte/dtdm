-- Mo rong 3 (tuy chon): cac truy van CRUD mau
-- Chay:  docker exec -i relational-database-server mariadb -uroot -proot < relational-database-server/crud-demo.sql
USE studentdb;

-- READ
SELECT * FROM students;

-- CREATE
INSERT INTO students(student_id, fullname, dob, major) VALUES ('SV004', 'Pham Thi D', '2002-01-09', 'Information Systems');
SELECT * FROM students WHERE student_id = 'SV004';

-- UPDATE
UPDATE students SET major = 'Artificial Intelligence' WHERE student_id = 'SV004';
SELECT * FROM students WHERE student_id = 'SV004';

-- DELETE
DELETE FROM students WHERE student_id = 'SV004';
SELECT COUNT(*) AS total_students FROM students;
