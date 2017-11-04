/* User */

INSERT INTO user (id, email, password, name, gender, contact, date_of_birth, is_campus, is_registered)
    VALUES (49524950, 'test@test.com','test','Tester','M','123-456-7890','2000-01-01','NO', 'YES');
INSERT INTO user (id, email, password, name, gender, contact, date_of_birth, is_campus, is_registered)
    VALUES (49382932, 'taylor.edu','test','Taylor University','M','123-321-7890','1830-04-29','YES', 'YES');

INSERT INTO user_campus (id, is_student, major, class_year, department, position)
    VALUES (49382932, 'NO', NULL, NULL, 'Computer Science & Engineering', 'Assistant');




/* Job */

INSERT INTO job (id, user_id, title, description, term, start_date, end_date, start_time, end_time, day, money, every)
    VALUES (12345555, 49382932,'Web Design Grader','Should grade assignments', 'SHORT','2017-10-01','2017-10-05', '09:00', '15:00', NULL, 12000, 'ONE TIME');
INSERT INTO job (id, user_id, title, description, term, start_date, end_date, start_time, end_time, day, money, every)
    VALUES (41235555, 49382932,'Computer Science TA','Should lead study table', 'LONG', NULL, NULL, '10:00', '12:00', '0/1/0/1/0/1/0', 880, 'HOUR');


/* Tag */

INSERT INTO tag (id, description)
    VALUES (41239950, 'Python');
INSERT INTO tag (id, description)
    VALUES (58473987, 'C++');
INSERT INTO tag (id, description)
    VALUES (20958829, 'Patience');
INSERT INTO tag (id, description)
    VALUES (59183958, 'Confident');
INSERT INTO tag (id, description)
    VALUES (69283943, 'Flexible');


/* Job Tag */

INSERT INTO job_tag (job_id, tag_id)
    VALUES (12345555, 41239950);
INSERT INTO job_tag (job_id, tag_id)
    VALUES (12345555, 58473987);
INSERT INTO job_tag (job_id, tag_id)
    VALUES (41235555, 20958829);
INSERT INTO job_tag (job_id, tag_id)
    VALUES (41235555, 69283943);
INSERT INTO job_tag (job_id, tag_id)
    VALUES (41235555, 59183958);
INSERT INTO job_tag (job_id, tag_id)
    VALUES (12345555, 59183958);