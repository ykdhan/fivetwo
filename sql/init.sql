/* User */

INSERT INTO user (id, email, password, first_name, last_name, gender, contact, date_of_birth, role)
    VALUES (49524950, 'david_han1@taylor.edu','test','David','Han','M','123-456-7890','04/08/1995','STUDENT');
INSERT INTO user (id, email, password, first_name, last_name, gender, contact, date_of_birth, role)
    VALUES (59385471, 'sungsoo_kim@taylor.edu','test','Sung','Kim','M','123-321-7890','04/28/1996','STUDENT');
INSERT INTO user (id, email, password, first_name, last_name, gender, contact, date_of_birth, role)
    VALUES (49382932, 'tu@taylor.edu','test','Taylor','University','M','123-321-7890','04/28/1830','STAFF');


/* Job */

INSERT INTO job (id, user_id, title, description, repeated, job_start_date, job_end_date, day, money, every, accepted)
    VALUES (39818513, 49382932,'Web Design Grader','Should grade assignments', 'FALSE','10/1/2017','10/5/2017', NULL, 12000, NULL, NULL);
INSERT INTO job (id, user_id, title, description, repeated, job_start_date, job_end_date, day, money, every, accepted)
    VALUES (39818550, 49382932,'Calculus TA','Should lead study table', 'TRUE', NULL, NULL, '0/1/0/1/0/1/0', 880, 'HOUR', NULL);
INSERT INTO job (id, user_id, title, description, repeated, job_start_date, job_end_date, day, money, every, accepted)
    VALUES (39398513, 49382932,'DC Crew','Should serve food', 'FALSE','10/1/2017','12/10/2017', NULL, 12000, NULL, NULL);
INSERT INTO job (id, user_id, title, description, repeated, job_start_date, job_end_date, day, money, every, accepted)
    VALUES (10818513, 49382932,'Church Worship Leader','Should lead worship', 'TRUE', NULL, NULL, '1/0/0/0/0/0/1', 9000, 'WEEK', NULL);
