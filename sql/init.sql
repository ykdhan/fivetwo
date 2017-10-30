/* User */

INSERT INTO user (id, email, password, name, gender, contact, date_of_birth, is_campus, is_registered)
    VALUES (49524950, 'david_han1@taylor.edu','test','David Han','M','123-456-7890','1995-10-08','NO', 'YES');
INSERT INTO user (id, email, password, name, gender, contact, date_of_birth, is_campus, is_registered)
    VALUES (59385471, 'sungsoo_kim@taylor.edu','test','Sung Kim','M','123-321-7890','2001-01-04','YES', 'YES');
INSERT INTO user (id, email, password, name, gender, contact, date_of_birth, is_campus, is_registered)
    VALUES (49382932, 'tu@taylor.edu','test','Taylor University','M','123-321-7890','1830-04-29','NO', 'YES');
INSERT INTO user (id, email, password, name, gender, contact, date_of_birth, is_campus, is_registered)
    VALUES (58373958, 'test@test.com','test','Tester','M','123-123-1230','2000-02-20','NO', 'YES');

INSERT INTO user_campus (id, is_student, major, class_year, department, position)
    VALUES (59385471, 'YES','Computer Science','Senior', NULL, NULL);





/* Job */

INSERT INTO job (id, user_id, title, description, term, start_date, end_date, start_time, end_time, day, money, every)
    VALUES (39818513, 49524950,'Web Design Grader','Should grade assignments', 'SHORT','2017-10-01','2017-10-05', '09:00', '15:00', NULL, 12000, 'ONE TIME');
INSERT INTO job (id, user_id, title, description, term, start_date, end_date, start_time, end_time, day, money, every)
    VALUES (39818550, 49524950,'Calculus TA','Should lead study table', 'LONG', NULL, NULL, '10:00', '12:00', '0/1/0/1/0/1/0', 880, 'HOUR');
INSERT INTO job (id, user_id, title, description, term, start_date, end_date, start_time, end_time, day, money, every)
    VALUES (39398513, 49382932,'DC Crew','Should serve food', 'SHORT','2017-10-01','2017-12-10', '13:00', '18:00', NULL, 12000, 'ONE TIME');
INSERT INTO job (id, user_id, title, description, term, start_date, end_date, start_time, end_time, day, money, every)
    VALUES (10818513, 49382932,'Church Worship Leader','Should lead worship', 'LONG', NULL, NULL, '09:30', '14:00', '1/0/0/0/0/0/1', 900, 'WEEK');


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
    VALUES (39818513, 41239950);
INSERT INTO job_tag (job_id, tag_id)
    VALUES (39818513, 58473987);
INSERT INTO job_tag (job_id, tag_id)
    VALUES (39818513, 20958829);
INSERT INTO job_tag (job_id, tag_id)
    VALUES (39398513, 69283943);
INSERT INTO job_tag (job_id, tag_id)
    VALUES (39398513, 59183958);
INSERT INTO job_tag (job_id, tag_id)
    VALUES (10818513, 59183958);