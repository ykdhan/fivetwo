import sqlite3
from flask import g
import datetime
import random

import os


# DB_PATH = '/var/www/52CO/52CO.sqlite'
DB_PATH = '52CO.sqlite'


# Connect to the database.
def connect_db():
    if not os.path.isfile(DB_PATH):
        raise RuntimeError("Can't find database file '{}'".format(DB_PATH))
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


# Open a database connection and hang on to it in the global object.
def open_db_connection():
    g.db = connect_db()


# If the database is open, close it.
def close_db_connection():
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


# Convert the 'row' retrieved with 'cursor' to a dictionary
# whose keys are column names and whose values are column values.
def row_to_dictionary(cursor, row):
    dictionary = {}
    for idx, col in enumerate(cursor.description):
        dictionary[col[0]] = row[idx]
    return dictionary

######################################


def user(id):
    u = g.db.execute('SELECT * FROM user WHERE id = ?', (id,)).fetchone()
    if u is None:
        return None
    if u['is_campus'] == 'YES':
        user = g.db.execute('SELECT * FROM user INNER JOIN user_campus ON user.id = user_campus.id WHERE user.id = ?', (id,)).fetchone()
    else:
        user = u
    return user


def have_user(email):
    return g.db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()


def user_info(email):
    u = g.db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()
    if u is None:
        return None
    if u['is_campus'] == 'YES':
        user = g.db.execute('SELECT * FROM user INNER JOIN user_campus ON user.id = user_campus.id WHERE user.id = ?', (u['id'],)).fetchone()
    else:
        user = u
    return user


def users():
    return g.db.execute('SELECT * FROM user').fetchall()


def sign_up(name, email, password, is_campus):
    user_id = random_id(8)

    if have_user(email) is None:
        signup = '''
                      INSERT INTO user (id, name, email, password, is_campus)
                     VALUES (:user_id, :name, :email, :password, :is_campus)
                     '''
        signup_cursor = g.db.execute(signup, {'user_id': user_id, 'name': name, 'email': email, 'password': password, 'is_campus': is_campus})
        g.db.commit()
        if signup_cursor.rowcount == 1:
            if is_campus == 'YES':
                campus = 'INSERT INTO user_campus (id) VALUES (:user_id)'
                campus_cursor = g.db.execute(campus, {'user_id': user_id})
                g.db.commit()
                if campus_cursor.rowcount != 1:
                    return 0
            return user_id
        else:
            return 0
    return 0


def sign_up_more(user_id, is_student, name, gender, contact, date_of_birth, major, year, department, position):
    birth = datetime.datetime.strptime(date_of_birth, '%m/%d/%Y').strftime("%Y-%m-%d")
    signup = 'UPDATE user SET gender = :gender, contact = :contact, date_of_birth = :birth WHERE id = :user_id'
    signup_cursor = g.db.execute(signup, {'user_id': user_id, 'gender': gender, 'contact': contact, 'birth': birth})
    g.db.commit()
    if signup_cursor.rowcount == 1:
        if is_student == 'YES':
            signup_name = 'UPDATE user SET name = :user_name WHERE id = :user_id'
            name_cursor = g.db.execute(signup_name, {'user_id': user_id, 'user_name': name})
            g.db.commit()
            student = '''
                            UPDATE user_campus SET is_student = :is_student, major = :major, class_year = :class_year
                            WHERE id = :user_id
                                 '''
            student_cursor = g.db.execute(student, {'user_id': user_id, 'is_student': is_student, 'major': major, 'class_year': year})
            g.db.commit()
            if student_cursor.rowcount != 1:
                return 0
        elif is_student == 'NO':
            signup_name = 'UPDATE user SET name = :user_name WHERE id = :user_id'
            name_cursor = g.db.execute(signup_name, {'user_id': user_id, 'user_name': name})
            g.db.commit()
            faculty = '''
                            UPDATE user_campus SET is_student = :is_student, department = :department, position = :position
                            WHERE id = :user_id
                                 '''
            faculty_cursor = g.db.execute(faculty, {'user_id': user_id, 'is_student': is_student, 'department': department, 'position': position})
            g.db.commit()
            if faculty_cursor.rowcount != 1:
                return 0
        register = 'UPDATE user SET is_registered = :register WHERE id = :user_id'
        register_cursor = g.db.execute(register, {'user_id': user_id, 'register': 'YES'})
        g.db.commit()
        if register_cursor.rowcount == 1:
            return 1
    return 0


def update_profile(user_id, is_student, name, gender, contact, date_of_birth, major, year, department, position, introduction):
    print('update')
    birth = datetime.datetime.strptime(date_of_birth, '%m/%d/%Y').strftime("%Y-%m-%d")
    update = 'UPDATE user SET name = :user_name, gender = :gender, contact = :contact, date_of_birth = :date_of_birth, introduction = :introduction WHERE id = :user_id'
    update_cursor = g.db.execute(update, {'user_id': user_id, 'user_name': name, 'gender': gender, 'contact': contact,
                                             'date_of_birth': birth, 'introduction': introduction})
    g.db.commit()
    if update_cursor.rowcount == 1:
        if is_student == 'YES':
            student = '''
                            UPDATE user_campus SET is_student = :is_student, major = :major, class_year = :class_year
                            WHERE id = :user_id
                                 '''
            student_cursor = g.db.execute(student, {'user_id': user_id, 'is_student': is_student, 'major': major, 'class_year': year})
            g.db.commit()
            if student_cursor.rowcount != 1:
                return 0
        elif is_student == 'NO':
            faculty = '''
                            UPDATE user_campus SET is_student = :is_student, department = :department, position = :position
                            WHERE id = :user_id
                                 '''
            faculty_cursor = g.db.execute(faculty, {'user_id': user_id, 'is_student': is_student, 'department': department, 'position': position})
            g.db.commit()
            if faculty_cursor.rowcount != 1:
                return 0
        return 1
    return 0


# generate random ID
def random_id(length):
    id = ""
    for i in range(length):
        id = id + str(random.randint(0,9))
    return id


# all available jobs
def jobs():
    return g.db.execute('SELECT * FROM job WHERE accepted = 0 ORDER BY created_at DESC').fetchall()


def search_jobs(keyword):
    search = '[[:<:]]'+keyword.lower()
    return g.db.execute('SELECT * FROM job WHERE accepted = 0 and lower(title) RLIKE ? ORDER BY created_at DESC',(search,)).fetchall()


# job information
def job(job_id):
    return g.db.execute('SELECT * FROM job WHERE id = ?', (job_id,)).fetchone()


# all connected tags to a job
def job_tags(job_id):
    return g.db.execute('SELECT * FROM job_tag INNER JOIN tag ON tag_id = tag.id WHERE job_id = ?', (job_id,)).fetchall()


# all connected questions to a job
def job_questions(job_id):
    return g.db.execute('SELECT * FROM question WHERE job_id = ?', (job_id,)).fetchall()


def job_answers(application_id):
    return g.db.execute('SELECT * FROM answer WHERE application_id = ?', (application_id,)).fetchall()


def job_applications(job_id):
    return g.db.execute('SELECT * FROM application WHERE job_id = ? ORDER BY created_at DESC', (job_id,)).fetchall()


def job_applied(job_id,user_id):
    applied = g.db.execute('SELECT * FROM application WHERE job_id = ? and user_id = ?', (job_id,user_id)).fetchall()
    if applied is not None:
        return True
    return False


def posts(user_id):
    return g.db.execute('SELECT * FROM job WHERE user_id = ? ORDER BY created_at DESC', (user_id,)).fetchall()


# post a new job
def post_job(user_id, title, description, term, start_date, end_date, start_time, end_time, workday, money, every, job_tags, job_questions):
    job_id = random_id(8)

    if term == 'LONG':
        start_date = None
        end_date = None
    else:
        day = None

    create = '''
              INSERT INTO job (id, user_id, title, description, term, start_date, end_date, start_time,
                                end_time, day, money, every)
             VALUES (:id, :user_id, :title, :description, :term, :start_date, :end_date, :start_time, :end_time, 
             :workday, :money, :every)
             '''
    post_cursor = g.db.execute(create, {'id': job_id, 'user_id': user_id, 'title': title, 'description': description,
                                   'term': term, 'start_date': start_date, 'end_date': end_date, 'start_time': start_time,
                                   'end_time': end_time, 'workday': workday, 'money': money, 'every': every})
    g.db.commit()
    if post_cursor.rowcount == 1:
        for tag in job_tags:
            tag_id = random_id(8)
            exist = g.db.execute('SELECT * FROM tag WHERE description = ?', (tag,)).fetchone()
            if exist is None:
                create = '''
                            INSERT INTO tag (id, description)
                            VALUES (:id, :description)
                            '''
                tag_cursor = g.db.execute(create, {'id': tag_id, 'description': tag})
                g.db.commit()
                if tag_cursor.rowcount == 1:
                    create = '''
                                INSERT INTO job_tag (job_id, tag_id)
                                VALUES (:job_id, :tag_id)
                                '''
                    job_tag_cursor = g.db.execute(create, {'job_id': job_id, 'tag_id': tag_id})
                    g.db.commit()
            else:
                create = '''
                            INSERT INTO job_tag (job_id, tag_id)
                            VALUES (:job_id, :tag_id)
                            '''
                job_tag_cursor = g.db.execute(create, {'job_id': job_id, 'tag_id': tag_id})
                g.db.commit()
        num = 1
        for question in job_questions:
            create = '''
                        INSERT INTO question (job_id, num, question)
                        VALUES (:job_id, :num, :question)
                        '''
            tag_cursor = g.db.execute(create, {'job_id': job_id, 'num': num, 'question': question})
            g.db.commit()
            num += 1
        return 1
    return 0


def applications(user_id):
    return g.db.execute('SELECT * FROM application WHERE user_id = ? ORDER BY created_at DESC', (user_id,)).fetchall()


# apply for a job
def apply_job(user_id, job_id, job_answers):
    application_id = random_id(8)

    create = '''
                  INSERT INTO application (id, user_id, job_id)
                 VALUES (:id, :user_id, :job_id)
                 '''
    app_cursor = g.db.execute(create, {'id': application_id, 'user_id': user_id, 'job_id': job_id})
    g.db.commit()
    if app_cursor.rowcount == 1:
        num = 1
        for answer in job_answers:
            print (answer)
            create = '''
                              INSERT INTO answer (application_id, num, answer)
                             VALUES (:app_id, :num, :answer)
                             '''
            ans_cursor = g.db.execute(create, {'app_id': application_id, 'num': num, 'answer': answer})
            g.db.commit()
            num += 1
        return 1
    return 0


def upload_profile(user_id, name):
    upload = 'UPDATE user SET profile_picture = :profile_picture WHERE id = :user_id'
    upload_cursor = g.db.execute(upload, {'user_id': user_id, 'profile_picture': name})
    g.db.commit()
    if upload_cursor.rowcount == 1:
        return 1
    return 0
