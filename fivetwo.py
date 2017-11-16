from flask import Flask, render_template, flash, redirect, url_for, request, session, jsonify
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField, IntegerField, PasswordField, BooleanField, HiddenField, TextAreaField
from wtforms.validators import Email, Length, NumberRange, DataRequired, InputRequired, EqualTo, AnyOf, Regexp, Optional
from flask_wtf import FlaskForm, validators
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_hashing import Hashing
import datetime
from flask_mail import Mail, Message
import string, random
import re
from flask_cas import CAS
from flask_cas import login
from flask_cas import logout
import os

import db

app = Flask(__name__)
hashing = Hashing(app)

cas = CAS(app, '/cas')
app.config['CAS_SERVER'] = 'https://sso.taylor.edu/'
app.config['CAS_AFTER_LOGIN'] = 'cas'

UPLOAD_FOLDER = os.path.basename('static/uploads/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config.update(
    DEBUG=True,
    # EMAIL SETTINGS
    MAIL_SERVER='smtp.mail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='fivetwo@mail.com',
    MAIL_PASSWORD='FiveTwo&52'
)
mail = Mail(app)
def send_email(recipients, title, text_body, html_body):
    msg = Message(title, sender='fivetwo@mail.com', recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

app.config['SECRET_KEY'] = '52CO Key'
app.config['WTF_CSRF_ENABLED'] = False


@app.before_request
def before():
    db.open_db_connection()


@app.teardown_request
def after(exception):
    db.close_db_connection()


# LOGIN
login_mgr = LoginManager(app)


# authenticates a user by taking their login and password and checking it against the user table.
def authenticate(email, password):
    for user in db.users():
        if user['is_campus'] == 'NO' and email == user['email']:
            if hashing.check_value(user['password'], password, salt='Five&Two52'):
                return email
    return None


def authenticate_id(user_id):
    for user in db.users():
        if user['is_campus'] == 'NO' and user_id == user['id']:
            print('user')
            return user['email']
    return None


# defines the user class which returns various values of the logged in user.
class User(object):
    def __init__(self, email):
        self.email = email
        self.name = db.user_info(email)['name']
        self.id = db.user_info(email)['id']
        self.picture = db.user_info(email)['profile_picture']
        self.is_registered = db.user_info(email)['is_registered']
        self.is_campus = db.user_info(email)['is_campus']
        if self.is_campus == 'YES':
            self.is_student = db.user_info(email)['is_student']
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return self.email

    def __repr__(self):
        return "<User '{}' {} {} {}>".format(self.email, self.is_authenticated, self.is_active, self.is_anonymous)


# Flask-Login calls this function on every request to recreate the current user object
# based on the unique ID it stored previously the session object.
@login_mgr.user_loader
def load_user(id):
    return User(id)


# application file that handles the login page.
@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    login_form = LoginForm()

    if login_form.is_submitted():
        print('LOGIN-----------------------------')
        if login_form.email.data == '':
            flash('Please fill out your email address.')
        elif len(login_form.email.data.split('@')) != 2:
            flash('Your email format is invalid.')
        elif login_form.email.data.split('@')[1] == 'taylor.edu':
            flash('Please log in as student/faculty.')
        elif login_form.password.data != '':
            email = login_form.email.data
            password = login_form.password.data
            if authenticate(email, password):
                user = User(email)
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('Your email address and password do not match.')
        else:
            flash('Please fill out your password.')

    return render_template('login.html', login_form=login_form, login=True)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    signup_form = SignUpForm()

    if signup_form.is_submitted():
        print('SIGNUP-----------------------------')
        if signup_form.new_name.data == '':
            flash('Please fill out your name.')
        elif signup_form.new_email.data == '':
            flash('Please fill out your email address.')
        elif len(signup_form.new_email.data.split('@')) != 2:
            flash('Your email format is invalid.')
        elif signup_form.new_email.data.split('@')[1] == 'taylor.edu':
            flash('Please log in as student/faculty.')
        elif signup_form.new_password.data == '':
            flash('Please fill out your password.')
        elif signup_form.new_password.data == signup_form.new_cpassword.data:
            pw = hashing.hash_value(signup_form.new_password.data, salt='Five&Two52')
            rowcount = db.sign_up(signup_form.new_name.data, signup_form.new_email.data, pw, 'NO')
            if rowcount != 1:
                title = "Please verify your email"
                message = "Dear " + signup_form.new_name.data + ",\r\n\r\nThank you for registering!" + \
                          "\r\nIn order to continue, please verify your email by clicking the link below." + \
                          "\r\n\r\nhttp://127.0.0.1:5000/verify/" + rowcount + \
                          "\r\n\r\nSincerely," + "\r\nFiveTwo Co."
                html = '''
                    <!DOCTYPE html><html lang="en-us"><head>
                    <meta charset="utf-8">
                    <meta http-equiv="X-UA-Compatible" content="IE=edge">
                    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">
                    <link href="https://fonts.googleapis.com/css?family=Quicksand:300,400,500" rel="stylesheet">
                    <title></title>
                    <style>
                    body { width: 100%; height: 100%; background: none; padding: 1rem; margin: 0;
                        font-size: 0.9rem; font-family: 'Quicksand', sans-serif; font-weight: 500;
                        color: #474747; text-align: center; line-height: 1.5; }
                    p { margin: 0; padding: 0; margin-bottom: 0.5rem; text-align: left; }
                    button {
                        font-size: 0.9rem; font-family: 'Questrial', sans-serif;font-weight: 500;
                        width: auto; cursor: pointer; background: #fff;
                        border: 0.06rem solid #E55A5A; border-radius: 0.25rem; color: #E55A5A;
                        padding: 0.6rem 1rem; margin: 0; margin-top: 0.8rem; margin-bottom: 1rem; }
                    button:hover { background: #E55A5A; color: #fff; }
                    #frame { width: 100%; max-width: 400px; margin: 3rem auto; }
                    #logo { width: 3.6rem; height: auto; }
                    #dear { margin-top: 2.5rem; margin-bottom: 2.5rem; } 
                    #end-message { margin-top: 2.5rem;}        
                    #note { margin-top: 2rem; color: #cecece; font-size: 0.7rem; }
                    </style>
                    </head><body><div id="frame"><img id="logo" alt="FIVETWO" src="https://fivetwo.co/static/img/fivetwo.svg">
                    <p id="dear">Greetings from FiveTwo,</p><p>Thank you for verifying your e-mail address.<br>Please click the button below to complete the process.</p>
                    <p><a href="https://fivetwo.co/verify/''' + rowcount + '''"><button>Verify Email</button></a></p>
                    <p>If you did not request to have your email verified, you can safely ignore this email. Rest assured your customer account is safe.</p>
                    <p>With encryption, FiveTwo secures all user information and personal data.</p>
                    <p>Thanks for visiting FiveTwo!</p>
                    <p id="note">Note: When you verify your email address on this account, you'll be locked out all of other accounts associated with that email address. It won't be possible to sign into those other accounts without also verifying ownership of that email address.</p>
                    </div></body></html>
                    '''
                send_email([signup_form.new_email.data], title, message, html)
                return redirect(url_for('welcome', user_id=rowcount))
            else:
                flash("Error: Unable to sign up.")
        else:
            flash("Please confirm your password.")
    return render_template('login.html', signup_form=signup_form, login=True, register=True)


# app that handles the logout functionality.
@app.route('/logout')
@login_required
def logout():

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if current_user.is_campus == 'YES':
        logout_user()
        return redirect('/cas/logout')
    else:
        logout_user()
        return redirect(url_for('index'))


@app.route('/welcome/<user_id>', methods=['GET', 'POST'])
def welcome(user_id):

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    name = db.user(user_id)['name']
    email = db.user(user_id)['email']
    return render_template('welcome.html', name=name, email=email, not_registered=True)


@app.route('/cas')
def cas():
    username = session[app.config['CAS_USERNAME_SESSION_KEY']]
    fn, ln = username.split('_', 2)
    if ln[-1] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        ln = ln[:-1]
    name = fn.title()+" "+ln.title()
    print(db.have_user(username))
    if db.have_user(username) is None:
        rowcount = db.sign_up(name, username, 'Five&Two52', 'YES')
        print('new')
    else:
        print('existing')
    user = User(username)
    login_user(user)
    return redirect(url_for('index'))


@app.route('/', methods=["GET", "POST"])
def index():

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if current_user.is_registered == 'NO':
        return redirect(url_for('sign_up'))

    if current_user.is_campus == 'YES':
        community = False
    else:
        community = True

    jobs = db.jobs(community)
    outputs = []
    for j in jobs:
        job = {}
        job['id'] = j['id']
        job['user'] = {}
        job['user']['id'] = j['user_id']
        job['user']['name'] = db.user(j['user_id'])['name']
        job['user']['picture'] = db.user(j['user_id'])['profile_picture']
        job['title'] = j['title']
        job['date'] = j['created_at']
        job['description'] = j['description']
        job['term'] = j['term']

        if job['term'] == 'LONG':
            days = str(j['day']).split("/")
            job['day'] = days
        else:
            start_month = datetime.datetime.strptime(j['start_date'], '%Y-%m-%d').strftime("%b")
            start_day = int(datetime.datetime.strptime(j['start_date'], '%Y-%m-%d').strftime("%d"))
            start_year = datetime.datetime.strptime(j['start_date'], '%Y-%m-%d').strftime("%y")
            end_month = datetime.datetime.strptime(j['end_date'], '%Y-%m-%d').strftime("%b")
            end_day = int(datetime.datetime.strptime(j['end_date'], '%Y-%m-%d').strftime("%d"))
            end_year = datetime.datetime.strptime(j['end_date'], '%Y-%m-%d').strftime("%y")
            job['start_date'] = start_month+" "+str(start_day)
            job['end_date'] = end_month+" "+str(end_day)

        start_hour = int(datetime.datetime.strptime(j['start_time'], '%H:%M').strftime("%H"))
        start_minute = datetime.datetime.strptime(j['start_time'], '%H:%M').strftime("%M")
        start_ampm = "AM"
        end_hour = int(datetime.datetime.strptime(j['end_time'], '%H:%M').strftime("%H"))
        end_minute = datetime.datetime.strptime(j['end_time'], '%H:%M').strftime("%M")
        end_ampm = "AM"

        if start_hour == 12:
            start_ampm = "PM"
        elif start_hour > 12:
            start_hour -= 12
            start_ampm = "PM"
        if end_hour == 12:
            end_ampm = "PM"
        elif end_hour > 12:
            end_hour -= 12
            end_ampm = "PM"

        job['start_time'] = str(start_hour) + ":" + start_minute + " " + start_ampm
        job['end_time'] = str(end_hour) + ":" + end_minute + " " + end_ampm

        job['money'] = str(j['money'])
        job['every'] = j['every']
        create_day = int(datetime.datetime.strptime(j['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%d'))
        create_month = datetime.datetime.strptime(j['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%b')
        create_year = datetime.datetime.strptime(j['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%Y')
        job['created_at'] = create_month + " " + str(create_day) # + ", " + create_year

        tags = db.job_tags(job['id'])

        job['tags'] = tags
        outputs.append(job)
    return render_template('index.html', jobs=outputs)


@app.route('/search')
def search():
    try:
        jobs = db.search_jobs(request.args.get('search'))
        outputs = []
        for j in jobs:
            job = {}
            job['id'] = j['id']
            job['user'] = {}
            job['user']['id'] = j['user_id']
            job['user']['name'] = db.user(j['user_id'])['name']
            job['title'] = j['title']
            job['date'] = j['created_at']
            job['description'] = j['description']
            job['term'] = j['term']

            if job['term'] == 'LONG':
                days = str(j['day']).split("/")
                job['day'] = days
            else:
                start_month = datetime.datetime.strptime(j['start_date'], '%Y-%m-%d').strftime("%b")
                start_day = int(datetime.datetime.strptime(j['start_date'], '%Y-%m-%d').strftime("%d"))
                start_year = datetime.datetime.strptime(j['start_date'], '%Y-%m-%d').strftime("%y")
                end_month = datetime.datetime.strptime(j['end_date'], '%Y-%m-%d').strftime("%b")
                end_day = int(datetime.datetime.strptime(j['end_date'], '%Y-%m-%d').strftime("%d"))
                end_year = datetime.datetime.strptime(j['end_date'], '%Y-%m-%d').strftime("%y")
                job['start_date'] = start_month + " " + str(start_day)
                job['end_date'] = end_month + " " + str(end_day)

            start_hour = int(datetime.datetime.strptime(j['start_time'], '%H:%M').strftime("%H"))
            start_minute = datetime.datetime.strptime(j['start_time'], '%H:%M').strftime("%M")
            start_ampm = "AM"
            end_hour = int(datetime.datetime.strptime(j['end_time'], '%H:%M').strftime("%H"))
            end_minute = datetime.datetime.strptime(j['end_time'], '%H:%M').strftime("%M")
            end_ampm = "AM"

            if start_hour == 12:
                start_ampm = "PM"
            elif start_hour > 12:
                start_hour -= 12
                start_ampm = "PM"
            if end_hour == 12:
                end_ampm = "PM"
            elif end_hour > 12:
                end_hour -= 12
                end_ampm = "PM"

            if start_ampm == end_ampm:
                job['start_time'] = str(start_hour) + ":" + start_minute
                job['end_time'] = str(end_hour) + ":" + end_minute + " " + end_ampm
            else:
                job['start_time'] = str(start_hour) + ":" + start_minute + " " + start_ampm
                job['end_time'] = str(end_hour) + ":" + end_minute + " " + end_ampm

            job['money'] = str(j['money'])
            job['every'] = j['every']

            tags = db.job_tags(job['id'])

            job['tags'] = tags
            outputs.append(job)

        return jsonify(jobs=outputs)
    except ValueError:
        return str(ValueError)


@app.route('/job/<job_id>', methods=["GET", "POST"])
def job(job_id):
    today = datetime.datetime.today()

    applied = db.job_applied(job_id,current_user.id)
    expired = db.job_expired(job_id)

    num_applications = len(db.pending_applications(job_id))

    j = db.job(job_id)

    if j['user_id'] == current_user.id:
        employer = True
    else:
        employer = False

    job = {}
    job['id'] = j['id']
    job['user'] = {}
    job['user']['id'] = j['user_id']
    job['user']['name'] = db.user(j['user_id'])['name']
    job['user']['picture'] = db.user(j['user_id'])['profile_picture']
    job['only_campus'] = j['only_campus']
    job['title'] = j['title']
    job['description'] = j['description']
    job['term'] = j['term']

    if job['term'] == 'LONG':
        days = str(j['day']).split("/")
        job['day'] = days
    else:
        start_month = datetime.datetime.strptime(j['start_date'], '%Y-%m-%d').strftime("%b")
        start_day = int(datetime.datetime.strptime(j['start_date'], '%Y-%m-%d').strftime("%d"))
        start_year = datetime.datetime.strptime(j['start_date'], '%Y-%m-%d').strftime("%y")
        end_month = datetime.datetime.strptime(j['end_date'], '%Y-%m-%d').strftime("%b")
        end_day = int(datetime.datetime.strptime(j['end_date'], '%Y-%m-%d').strftime("%d"))
        end_year = datetime.datetime.strptime(j['end_date'], '%Y-%m-%d').strftime("%y")
        job['start_date'] = start_month + " " + str(start_day)
        job['end_date'] = end_month + " " + str(end_day)

    start_hour = int(datetime.datetime.strptime(j['start_time'], '%H:%M').strftime("%H"))
    start_minute = datetime.datetime.strptime(j['start_time'], '%H:%M').strftime("%M")
    start_ampm = "AM"
    end_hour = int(datetime.datetime.strptime(j['end_time'], '%H:%M').strftime("%H"))
    end_minute = datetime.datetime.strptime(j['end_time'], '%H:%M').strftime("%M")
    end_ampm = "AM"

    if start_hour == 12:
        start_ampm = "PM"
    elif start_hour > 12:
        start_hour -= 12
        start_ampm = "PM"
    if end_hour == 12:
        end_ampm = "PM"
    elif end_hour > 12:
        end_hour -= 12
        end_ampm = "PM"

    if start_ampm == end_ampm:
        job['start_time'] = str(start_hour) + ":" + start_minute
        job['end_time'] = str(end_hour) + ":" + end_minute + " " + end_ampm
    else:
        job['start_time'] = str(start_hour) + ":" + start_minute + " " + start_ampm
        job['end_time'] = str(end_hour) + ":" + end_minute + " " + end_ampm

    job['money'] = str(j['money'])
    job['every'] = j['every']
    create_day = int(datetime.datetime.strptime(j['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%d'))
    create_month = datetime.datetime.strptime(j['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%b')
    create_year = datetime.datetime.strptime(j['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%Y')
    job['created_at'] = create_month + " " + str(create_day) + ", " + create_year

    tags = db.job_tags(job_id)
    questions = db.job_questions(job_id)

    job['tags'] = tags
    job['questions'] = questions
    job['num_questions'] = len(questions)

    if employer:
        prev_tags = ''
        for t in tags:
            prev_tags += t['description'] + '#'
        prev_questions = ''
        for q in questions:
            prev_questions += q['question'] + '#'
        if job['term'] == 'LONG':
            job_form = EditForm(title=job['title'],
                                only_campus=job['only_campus'],
                                description=job['description'],
                                questions=prev_questions,
                                tags=prev_tags,
                                term=job['term'],
                                start_time=str(start_hour) + ":" + start_minute,
                                end_time=str(end_hour) + ":" + end_minute,
                                start_ampm=start_ampm,
                                end_ampm=end_ampm,
                                day=j['day'],
                                wage=job['money'],
                                every=job['every']
                                )
        else:
            job_form = EditForm(title=job['title'],
                                only_campus=job['only_campus'],
                                description=job['description'],
                                questions=prev_questions,
                                tags=prev_tags,
                                term=job['term'],
                                start_date=datetime.datetime.strptime(j['start_date'], '%Y-%m-%d').strftime("%m/%d/%Y"),
                                end_date=datetime.datetime.strptime(j['end_date'], '%Y-%m-%d').strftime("%m/%d/%Y"),
                                start_time=str(start_hour) + ":" + start_minute,
                                end_time=str(end_hour) + ":" + end_minute,
                                start_ampm=start_ampm,
                                end_ampm=end_ampm,
                                wage=job['money'],
                                every=job['every']
                                )

        if job_form.validate_on_submit():

            if job_form.title.data == '':
                flash('Please fill out the title.')
            elif job_form.term.data == 'LONG' and job_form.day.data == '0/0/0/0/0/0/0':
                flash('Please select the days.')
            elif job_form.term.data == 'SHORT' and (job_form.start_date.data == '' or job_form.end_date.data == ''):
                flash('Please fill out the dates.')
            elif job_form.term.data == 'SHORT' and (
                not re.search('^\d{2}/\d{2}/\d{4}$', job_form.start_date.data) or not re.search('^\d{2}/\d{2}/\d{4}$',
                                                                                                job_form.end_date.data)):
                flash('Please check your date format. (mm/dd/yyyy)')
            elif job_form.start_time.data == '' or job_form.end_time.data == '':
                flash('Please fill out the times.')
            elif job_form.wage.data == '':
                flash('Please fill out the wage.')
            else:

                if job_form.term.data == 'LONG':
                    edit_start_date = None
                    edit_end_date = None
                else:
                    edit_start_date = datetime.datetime.strptime(job_form.start_date.data, '%m/%d/%Y').strftime("%Y-%m-%d")
                    edit_end_date = datetime.datetime.strptime(job_form.end_date.data, '%m/%d/%Y').strftime("%Y-%m-%d")

                edit_start_time = job_form.start_time.data
                if int(edit_start_time.split(':')[0]) >= 12:
                    edit_start_time = '12:' + edit_start_time.split(':')[1]
                if int(edit_start_time.split(':')[1]) >= 60:
                    edit_start_time = edit_start_time.split(':')[0] + ':00'

                edit_end_time = job_form.end_time.data
                if int(edit_end_time.split(':')[0]) >= 12:
                    edit_end_time = '12:' + edit_end_time.split(':')[1]
                if int(edit_end_time.split(':')[1]) >= 60:
                    edit_end_time = edit_end_time.split(':')[0] + ':00'

                if job_form.start_ampm.data == 'PM':
                    if int(edit_start_time.split(':')[0]) < 12:
                        start_hour = int(edit_start_time.split(':')[0]) + 12
                    else:
                        start_hour = int(edit_start_time.split(':')[0])
                    edit_start_time = str(start_hour) + ':' + edit_start_time.split(':')[1]
                if job_form.end_ampm.data == 'PM':
                    if int(edit_end_time.split(':')[0]) < 12:
                        end_hour = int(edit_end_time.split(':')[0]) + 12
                    else:
                        end_hour = int(edit_end_time.split(':')[0])
                    edit_end_time = str(end_hour) + ':' + edit_end_time.split(':')[1]

                tags = []
                tag_data = job_form.tags.data.split("#")
                for t in tag_data:
                    if t != '':
                        tags.append(t)
                questions = []
                question_data = job_form.questions.data.split("#")
                for q in question_data:
                    if q != '':
                        questions.append(q)

                #edit_start_time = job_form.start_time.data
                #edit_end_time = job_form.end_time.data
                #if job_form.start_ampm.data == 'PM':
                #    edit_start_time = str(int(job_form.start_time.data.split(':')[0]) + 12) + ':' + job_form.start_time.data.split(':')[1]
                #if job_form.end_ampm.data == 'PM':
                #    edit_end_time = str(int(job_form.end_time.data.split(':')[0]) + 12) + ':' + job_form.end_time.data.split(':')[1]

                rowcount = db.edit_job(job_id, job_form.title.data, job_form.description.data,
                                       job_form.term.data, edit_start_date, edit_end_date,
                                       edit_start_time, edit_end_time, job_form.day.data,
                                       int(job_form.wage.data), job_form.every.data, tags, questions,
                                       job_form.only_campus.data)
                if rowcount == 1:
                    flash("Your job has been edited.")
                else:
                    flash("Error: Cannot edit job.")

    else:
        job_form = JobForm()

        if job_form.validate_on_submit():

            #answers = []
            #for a in job_form.answers.data.split('#'):
            #    answers.append(a)

            print(job_form.answers.data)
            rowcount = db.apply_job(current_user.id, job_id, job_form.answers.data)

            if rowcount == 1:
                return redirect(url_for('applications'))
            else:
                flash("Error: Cannot apply.")

    return render_template('job.html', job=job, form=job_form, today=today, applied=applied, expired=expired, employer=employer, num_applications=num_applications)


@app.route('/job/<job_id>/applications', methods=["GET", "POST"])
def job_applications(job_id):
    job_applications = db.job_applications(job_id)
    print(job_applications)
    outputs = []
    for a in job_applications:
        application = {}
        user = db.user(a['user_id'])
        application['status'] = a['status']
        application['id'] = a['id']
        application['date'] = datetime.datetime.strptime(a['apply_date'], '%Y-%m-%d %H:%M:%S').strftime("%b %d, %Y")
        application['user'] = {}
        application['user']['name'] = user['name']
        application['user']['picture'] = user['profile_picture']
        application['user']['gender'] = user['gender']
        application['user']['introduction'] = user['introduction']
        application['user']['contact'] = user['contact']
        application['user']['email'] = user['email']
        application['user']['age'] = ''
        if user['date_of_birth'] != None and user['date_of_birth'] != "":
            birth = datetime.datetime.strptime(user['date_of_birth'], '%Y-%m-%d')
            today = datetime.datetime.today()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            application['user']['age'] = age
        application['user']['picture'] = user['profile_picture']
        application['user']['is_campus'] = user['is_campus']
        if user['is_campus'] == 'YES':
            application['user']['is_student'] = user['is_student']
            if user['is_student'] == 'YES':
                application['user']['major'] = user['major']
                application['user']['year'] = user['class_year']
            else:
                application['user']['department'] = user['department']
                application['user']['position'] = user['position']
        questions = []
        num = 0
        for i in db.job_questions(job_id):
            q = {}
            q['question'] = i['question']
            q['answer'] = db.job_answers(a['id'])[num]['answer']
            questions.append(q)
            num += 1
        application['questions'] = questions
        outputs.append(application)
    print(outputs)

    return render_template('job-applications.html', applications=outputs)


@app.route('/job/<job_id>/delete', methods=["GET", "POST"])
def delete(job_id):
    employer = db.job(job_id)['user_id']
    if employer == current_user.id:
        delete = db.delete(job_id)
        return jsonify(delete)
    return 0


@app.route('/accept/<application_id>', methods=['POST'])
def accept(application_id):

    # check if inputs are valid
    job_id = db.application(application_id)['job_id']
    employer = db.job(job_id)['user_id']
    if employer == current_user.id:
        accept = db.accept(application_id)

        if accept == 1:
            a = db.application(application_id)

            title = "Your application has been accepted."
            message = "Dear " + a['name'] + ",\r\n\r\nCongratulations!" + \
                      "\r\nYour application has been reviewed and accepted by your employer." + \
                      "\r\nYou will soon receive a call or email from your employer for more details." + \
                      "\r\nThank you for using FiveTwo." \
                      "\r\n\r\nSincerely," + "\r\nFiveTwo Co."
            html = '''
                <!DOCTYPE html><html lang="en-us"><head>
                <meta charset="utf-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">
                <link href="https://fonts.googleapis.com/css?family=Quicksand:300,400,500" rel="stylesheet">
                <title></title>
                <style>
                body { width: 100%; height: 100%; background: none; padding: 1rem; margin: 0;
                    font-size: 0.9rem; font-family: 'Quicksand', sans-serif; font-weight: 500;
                    color: #474747; text-align: center; line-height: 1.5; }
                p { margin: 0; padding: 0; margin-bottom: 0.5rem; text-align: left; }
                button {
                    font-size: 0.9rem; font-family: 'Questrial', sans-serif;font-weight: 500;
                    width: auto; cursor: pointer; background: #fff;
                    border: 0.06rem solid #E55A5A; border-radius: 0.25rem; color: #E55A5A;
                    padding: 0.6rem 1rem; margin: 0; margin-top: 0.8rem; margin-bottom: 1rem; }
                button:hover { background: #E55A5A; color: #fff; }
                #frame { width: 100%; max-width: 400px; margin: 3rem auto; }
                #logo { width: 3.6rem; height: auto; }
                #dear { margin-top: 2.5rem; margin-bottom: 2.5rem; } 
                #end-message { margin-top: 2.5rem;}        
                #note { margin-top: 2rem; color: #cecece; font-size: 0.7rem; }
                </style>
                </head><body><div id="frame"><img id="logo" alt="FIVETWO" src="https://fivetwo.co/static/img/fivetwo.svg">
                <p id="dear">Dear ''' + a['name'] + ''',</p><p>Congratulations!</p><p>Your application has been reviewed and accepted by your employer.</p>
                <p>You will soon receive a call or email from your employer for more details.</p>
                <p>To review your application, please click the button below.</p>
                <p><a href="https://fivetwo.co/applications"><button>Review Application</button></a></p>
                <p>Thank you for using FiveTwo!</p>
                <p id="note">Note: This is not the end of application process. Your employer will direct you to the next steps.</p>
                </div></body></html>
                '''
            send_email([a['email']], title, message, html)
        return jsonify(accept)
    return jsonify(0)


@app.route('/decline/<application_id>', methods=['POST'])
def decline(application_id):

    # check if inputs are valid
    job_id = db.application(application_id)['job_id']
    employer = db.job(job_id)['user_id']

    if employer == current_user.id:
        decline = db.decline(application_id)

        return jsonify(decline)
    return jsonify(0)


@app.route('/new', methods=["GET", "POST"])
def new():
    day = int(datetime.datetime.today().strftime('%d'))
    month = datetime.datetime.today().strftime('%b')
    year = datetime.datetime.today().strftime('%Y')

    today = month+" "+str(day)+", "+year

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    post_form = PostForm()

    if post_form.validate_on_submit():
        print('Title:'+str(post_form.title.data))
        print('Description:'+str(post_form.description.data))
        print('Wage:'+str(post_form.wage.data))
        print('Every:'+str(post_form.every.data))
        print('StartDate:'+str(post_form.start_date.data))
        print('EndDate:'+str(post_form.end_date.data))
        print('StartTime:'+str(post_form.start_time.data))
        print('EndTime:'+str(post_form.end_time.data))
        print('Day:'+str(post_form.day.data))
        print('Tags:'+str(post_form.tags.data))
        print('Questions:'+str(post_form.questions.data))
        print('Only Campus:'+str(post_form.only_campus.data))
        print('Term:'+str(post_form.term.data))

        valid = True
        error = []

        if post_form.title.data == '':
            flash('Please fill out the title.')
        elif post_form.term.data == 'LONG' and post_form.day.data == '0/0/0/0/0/0/0':
            flash('Please select the days.')
        elif post_form.term.data == 'SHORT' and (post_form.start_date.data == '' or post_form.end_date.data == ''):
            flash('Please fill out the dates.')
        elif post_form.term.data == 'SHORT' and (not re.search('^\d{2}/\d{2}/\d{4}$', post_form.start_date.data) or not re.search('^\d{2}/\d{2}/\d{4}$', post_form.end_date.data)):
            flash('Please check your date format. (mm/dd/yyyy)')
        elif post_form.start_time.data == '' or post_form.end_time.data == '':
            flash('Please fill out the times.')
        elif post_form.wage.data == '':
            flash('Please fill out the wage.')
        else:
            if post_form.term.data == 'LONG':
                start_date = None
                end_date = None
            else:
                start_date = datetime.datetime.strptime(post_form.start_date.data, '%m/%d/%Y').strftime("%Y-%m-%d")
                end_date = datetime.datetime.strptime(post_form.end_date.data, '%m/%d/%Y').strftime("%Y-%m-%d")

            start_time = post_form.start_time.data
            print('start before: '+start_time)
            if int(start_time.split(':')[0]) >= 12:
                start_time = '12:'+start_time.split(':')[1]
            if int(start_time.split(':')[1]) >= 60:
                start_time = start_time.split(':')[0] + ':00'
            print('start after: ' + start_time)

            end_time = post_form.end_time.data
            print('end before: ' + end_time)
            if int(end_time.split(':')[0]) >= 12:
                end_time = '12:'+end_time.split(':')[1]
            if int(end_time.split(':')[1]) >= 60:
                end_time = end_time.split(':')[0] + ':00'
            print('end before: ' + end_time)

            if post_form.start_ampm.data == 'PM':
                if int(start_time.split(':')[0]) < 12:
                    start_hour = int(start_time.split(':')[0]) + 12
                    print('less than 12')
                else:
                    start_hour = int(start_time.split(':')[0])
                    print('it is 12')
                start_time = str(start_hour) + ':' + start_time.split(':')[1]
            if post_form.end_ampm.data == 'PM':
                if int(end_time.split(':')[0]) < 12:
                    end_hour = int(end_time.split(':')[0]) + 12
                    print('less than 12')
                else:
                    end_hour = int(end_time.split(':')[0])
                    print('it is 12')
                end_time = str(end_hour) + ':' + end_time.split(':')[1]

            tags = []
            tag_data = post_form.tags.data.split("#")
            for t in tag_data:
                if t != '':
                    tags.append(t)
            questions = []
            question_data = post_form.questions.data.split("#")
            for q in question_data:
                if q != '':
                    questions.append(q)

            rowcount = db.post_job(current_user.id, post_form.title.data, post_form.description.data, post_form.term.data, start_date,
                               end_date, start_time, end_time, post_form.day.data,
                               int(post_form.wage.data), post_form.every.data, tags, questions, post_form.only_campus.data)
            if rowcount == 1:
                return redirect(url_for('index'))
            else:
                flash("Error: Cannot post new job.")

    return render_template('new.html', form=post_form, today=today)


@app.route('/posts', methods=["GET", "POST"])
def posts():

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    jobs = db.posts(current_user.id)

    outputs = []
    for j in jobs:
        job = {}
        job['id'] = j['id']
        job['user'] = {}
        job['user']['id'] = j['user_id']
        job['user']['name'] = db.user(j['user_id'])['name']
        job['title'] = j['title']
        job['date'] = j['created_at']
        job['description'] = j['description']
        job['term'] = j['term']

        if job['term'] == 'LONG':
            days = str(j['day']).split("/")
            job['day'] = days
        else:
            start_month = datetime.datetime.strptime(j['start_date'], '%Y-%m-%d').strftime("%b")
            start_day = int(datetime.datetime.strptime(j['start_date'], '%Y-%m-%d').strftime("%d"))
            start_year = datetime.datetime.strptime(j['start_date'], '%Y-%m-%d').strftime("%y")
            end_month = datetime.datetime.strptime(j['end_date'], '%Y-%m-%d').strftime("%b")
            end_day = int(datetime.datetime.strptime(j['end_date'], '%Y-%m-%d').strftime("%d"))
            end_year = datetime.datetime.strptime(j['end_date'], '%Y-%m-%d').strftime("%y")
            job['start_date'] = start_month + " " + str(start_day)
            job['end_date'] = end_month + " " + str(end_day)


        start_hour = int(datetime.datetime.strptime(j['start_time'], '%H:%M').strftime("%H"))
        start_minute = datetime.datetime.strptime(j['start_time'], '%H:%M').strftime("%M")
        start_ampm = "AM"
        end_hour = int(datetime.datetime.strptime(j['end_time'], '%H:%M').strftime("%H"))
        end_minute = datetime.datetime.strptime(j['end_time'], '%H:%M').strftime("%M")
        end_ampm = "AM"

        if start_hour == 12:
            start_ampm = "PM"
        elif start_hour > 12:
            start_hour -= 12
            start_ampm = "PM"
        if end_hour == 12:
            end_ampm = "PM"
        elif end_hour > 12:
            end_hour -= 12
            end_ampm = "PM"

        if start_ampm == end_ampm:
            job['start_time'] = str(start_hour) + ":" + start_minute
            job['end_time'] = str(end_hour) + ":" + end_minute + " " + end_ampm
        else:
            job['start_time'] = str(start_hour) + ":" + start_minute + " " + start_ampm
            job['end_time'] = str(end_hour) + ":" + end_minute + " " + end_ampm

        job['money'] = str(j['money'])
        job['every'] = j['every']
        create_day = int(datetime.datetime.strptime(j['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%d'))
        create_month = datetime.datetime.strptime(j['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%b')
        create_year = datetime.datetime.strptime(j['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%Y')
        job['created_at'] = create_month + " " + str(create_day) + ", " + create_year

        tags = db.job_tags(job['id'])

        job['tags'] = tags
        job['num_applications'] = len(db.pending_applications(j['id']))
        job['expired'] = j['expired']
        outputs.append(job)
    return render_template('posts.html', jobs=outputs)


@app.route('/applications', methods=["GET", "POST"])
def applications():

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    applications = db.applications(current_user.id)

    outputs = []
    for a in applications:
        apply = {}
        j = db.job(a['job_id'])
        job = {}
        job['user'] = {}
        job['user']['id'] = j['user_id']
        job['user']['name'] = db.user(j['user_id'])['name']
        job['user']['picture'] = db.user(j['user_id'])['profile_picture']
        job['title'] = j['title']
        job['date'] = j['created_at']
        job['description'] = j['description']
        job['term'] = j['term']

        if job['term'] == 'LONG':
            days = str(j['day']).split("/")
            job['day'] = days
        else:
            start_month = datetime.datetime.strptime(j['start_date'], '%Y-%m-%d').strftime("%b")
            start_day = int(datetime.datetime.strptime(j['start_date'], '%Y-%m-%d').strftime("%d"))
            start_year = datetime.datetime.strptime(j['start_date'], '%Y-%m-%d').strftime("%y")
            end_month = datetime.datetime.strptime(j['end_date'], '%Y-%m-%d').strftime("%b")
            end_day = int(datetime.datetime.strptime(j['end_date'], '%Y-%m-%d').strftime("%d"))
            end_year = datetime.datetime.strptime(j['end_date'], '%Y-%m-%d').strftime("%y")
            job['start_date'] = start_month + " " + str(start_day)
            job['end_date'] = end_month + " " + str(end_day)

        start_hour = int(datetime.datetime.strptime(j['start_time'], '%H:%M').strftime("%H"))
        start_minute = datetime.datetime.strptime(j['start_time'], '%H:%M').strftime("%M")
        start_ampm = "AM"
        end_hour = int(datetime.datetime.strptime(j['end_time'], '%H:%M').strftime("%H"))
        end_minute = datetime.datetime.strptime(j['end_time'], '%H:%M').strftime("%M")
        end_ampm = "AM"

        if start_hour == 12:
            start_ampm = "PM"
        elif start_hour > 12:
            start_hour -= 12
            start_ampm = "PM"
        if end_hour == 12:
            end_ampm = "PM"
        elif end_hour > 12:
            end_hour -= 12
            end_ampm = "PM"

        if start_ampm == end_ampm:
            job['start_time'] = str(start_hour) + ":" + start_minute
            job['end_time'] = str(end_hour) + ":" + end_minute + " " + end_ampm
        else:
            job['start_time'] = str(start_hour) + ":" + start_minute + " " + start_ampm
            job['end_time'] = str(end_hour) + ":" + end_minute + " " + end_ampm

        job['money'] = str(j['money'])
        job['every'] = j['every']
        create_day = int(datetime.datetime.strptime(j['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%d'))
        create_month = datetime.datetime.strptime(j['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%b')
        create_year = datetime.datetime.strptime(j['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%Y')
        job['created_at'] = create_month + " " + str(create_day) + ", " + create_year

        tags = db.job_tags(j['id'])

        job['tags'] = tags

        questions = []
        num = 0
        for i in db.job_questions(j['id']):
            q = {}
            q['question'] = i['question']
            q['answer'] = db.job_answers(a['id'])[num]['answer']
            questions.append(q)
            num += 1
        apply['questions'] = questions
        apply['job'] = job
        apply['status'] = a['status']
        apply['date'] = datetime.datetime.strptime(a['created_at'], '%Y-%m-%d %H:%M:%S').strftime("%b %d, %Y")

        outputs.append(apply)

    return render_template('applications.html', applications=outputs)


@app.route('/sign-up', methods=["GET", "POST"])
def sign_up():

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    user = db.user(current_user.id)
    if db.user(current_user.id) is None:
        return redirect(url_for('index'))
    if user['is_campus'] == 'YES':
        signup_form = SignUpMoreFormCampus(name=current_user.name)
        is_campus = True
    else:
        signup_form = SignUpMoreForm()
        is_campus = False

    if signup_form.is_submitted():

        if is_campus and signup_form.name.data == '':
            flash('Please fill out your name.')
        elif signup_form.contact.data != '' and not re.search('^\d{3}-\d{3}-\d{4}$', signup_form.contact.data):
            flash('Please check your contact format. (123-456-7890)')
        elif signup_form.birth.data == '':
            flash('Please fill out your date of bith.')
        elif not re.search('^\d{2}/\d{2}/\d{4}$', signup_form.birth.data):
            flash('Please check your date format. (mm/dd/yyyy)')
        else:
            if is_campus:
                if signup_form.is_student.data == 'NO':
                    is_student = False
                else:
                    is_student = True
                if is_student:
                    rowcount = db.sign_up_more(current_user.id, 'YES',
                                                   signup_form.name.data,
                                                   signup_form.gender.data,
                                                   signup_form.contact.data,
                                                   signup_form.birth.data,
                                                   signup_form.major.data,
                                                   signup_form.year.data,
                                                   None,
                                                   None)
                else:
                    rowcount = db.sign_up_more(current_user.id, 'NO',
                                               signup_form.name.data,
                                               signup_form.gender.data,
                                               signup_form.contact.data,
                                               signup_form.birth.data,
                                               None,
                                               None,
                                               signup_form.department.data,
                                               signup_form.position.data)
            else:
                rowcount = db.sign_up_more(current_user.id, None,
                                           None,
                                           signup_form.gender.data,
                                           signup_form.contact.data,
                                           signup_form.birth.data,
                                           None, None, None, None)
            if rowcount == 1:
                return redirect(url_for('index'))
            else:
                flash("Error: Unable to sign up.")

    return render_template('sign-up.html', signup_form=signup_form, is_campus=is_campus, not_registered=True)


@app.route('/verify/<user_id>', methods=["GET", "POST"])
def verify(user_id):

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    signup_form = SignUpMoreForm()
    if signup_form.validate_on_submit():
        rowcount = db.sign_up_more(user_id, None,
                                   None,
                                   signup_form.gender.data,
                                   signup_form.contact.data,
                                   signup_form.birth.data,
                                   None, None, None, None)
        if rowcount == 1:
            user = User(db.user(user_id)['email'])
            login_user(user)
            return redirect(url_for('index'))
            flash("Error: Cannot authenticate.")
        else:
            flash("Error: Cannot verify.")

    return render_template('verify.html', signup_form=signup_form, not_registered=True)


@app.route('/profile', methods=["GET", "POST"])
def profile():

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    user = db.user(current_user.id)
    if user['introduction'] is None:
        introduction = ""
    else:
        introduction = user['introduction']
    if user['is_campus'] == 'NO':
        profile_form = ProfileForm(name=user['name'], gender=user['gender'], contact=user['contact'],
                               birth=datetime.datetime.strptime(user['date_of_birth'], '%Y-%m-%d').strftime("%m/%d/%Y"),
                                   introduction=introduction)
    else:
        if user['is_student'] == 'YES':
            profile_form = ProfileForm(name=user['name'], gender=user['gender'], contact=user['contact'],
                                       birth=datetime.datetime.strptime(user['date_of_birth'], '%Y-%m-%d').strftime(
                                           "%m/%d/%Y"), major=user['major'], year=user['class_year'],
                                       introduction=introduction)
        else:
            profile_form = ProfileForm(name=user['name'], gender=user['gender'], contact=user['contact'],
                                       birth=datetime.datetime.strptime(user['date_of_birth'], '%Y-%m-%d').strftime(
                                           "%m/%d/%Y"), department=user['department'], position=user['position'],
                                       introduction=introduction)

    if profile_form.is_submitted():

        if profile_form.name.data == '':
            flash('Please fill out your name.')
        elif profile_form.contact.data != '' and not re.search('^\d{3}-\d{3}-\d{4}$', profile_form.contact.data):
            flash('Please check your contact format. (123-456-7890)')
        elif profile_form.birth.data == '':
            flash('Please fill out your date of bith.')
        elif not re.search('^\d{2}/\d{2}/\d{4}$', profile_form.birth.data):
            flash('Please check your date format. (mm/dd/yyyy)')
        else:

            if current_user.is_campus == 'YES':
                if current_user.is_student == 'YES':
                    rowcount = db.update_profile(current_user.id, 'YES', profile_form.name.data, profile_form.gender.data,
                                             profile_form.contact.data, profile_form.birth.data, profile_form.major.data, profile_form.year.data,
                                             None, None, profile_form.introduction.data)
                else:
                    rowcount = db.update_profile(current_user.id, 'NO', profile_form.name.data, profile_form.gender.data,
                                                 profile_form.contact.data, profile_form.birth.data,
                                                 None, None,
                                                 profile_form.department.data, profile_form.position.data,
                                                 profile_form.introduction.data)
            else:
                rowcount = db.update_profile(current_user.id, None, profile_form.name.data, profile_form.gender.data,
                                             profile_form.contact.data, profile_form.birth.data, None, None, None, None,
                                             profile_form.introduction.data)

            if rowcount == 1:
                return redirect(url_for('profile'))
            else:
                flash("Error: Cannot update profile.")

    return render_template('profile.html', profile_form=profile_form)


@app.route('/upload-profile', methods=['POST'])
def upload_profile():
    id = ""
    for i in range(15):
        id = id + str(random.randint(0, 9))
    file = request.files['input-image']
    name = id+'.'+file.filename.split('.')[-1]
    print(name)
    f = os.path.join('static/profiles', name)
    print(f)
    file.save(f)
    db.upload_profile(current_user.id, name)
    data = 1
    return jsonify(data)


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    login_submit = SubmitField('Sign In')


class SignUpForm(FlaskForm):
    new_name = StringField('Name')
    new_email = StringField('Email Address')
    new_password = PasswordField('Password')
    new_cpassword = PasswordField('Confirm Password')
    signup_submit = SubmitField('Sign Up')


class SignUpMoreForm(FlaskForm):
    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female')])
    contact = StringField('Email Address')
    birth = StringField('Date of Birth')
    signup_submit = SubmitField('Sign Up')


class SignUpMoreFormCampus(FlaskForm):
    is_student = HiddenField('Is Student')
    name = StringField('Name')
    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female')])
    contact = StringField('Email Address')
    birth = StringField('Date of Birth')
    major = StringField('Major')
    year = SelectField('Class Year', choices=[('Freshman', 'Freshman'), ('Sophomore', 'Sophomore'), ('Junior', 'Junior'), ('Senior', 'Senior')])
    department = StringField('Department')
    position = StringField('Position')
    signup_submit = SubmitField('Sign Up')


class ProfileForm(FlaskForm):
    picture = HiddenField('Profile Picture')
    name = StringField('Name')
    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female')])
    contact = StringField('Email Address')
    birth = StringField('Date of Birth')
    major = StringField('Major')
    year = SelectField('Class Year', choices=[('Freshman', 'Freshman'), ('Sophomore', 'Sophomore'), ('Junior', 'Junior'), ('Senior', 'Senior')])
    department = StringField('Department')
    position = StringField('Position')
    introduction = TextAreaField('Introduction')
    submit = SubmitField('Update Profile')


class PostForm(FlaskForm):
    title = StringField('Title')
    only_campus = HiddenField('Only Campus')
    description = TextAreaField('Description')
    questions = HiddenField('Questions')
    term = HiddenField('Term')
    start_date = StringField('Start Date')
    end_date = StringField('End Date')
    start_time = StringField('Start Time')
    end_time = StringField('End Time')
    start_ampm = SelectField('Start AMPM', choices=[('AM', 'AM'), ('PM', 'PM')])
    end_ampm = SelectField('End AMPM', choices=[('AM', 'AM'), ('PM', 'PM')])
    day = HiddenField('Day')
    wage = HiddenField('Wage')
    every = SelectField('Every', choices=[("HOUR", "Hour"),("DAY", "Day"),("WEEK", "Week"),("MONTH", "Month"),("ONE TIME", "One Time")])
    tags = HiddenField('Tags')
    submit = SubmitField('Post')


class EditForm(FlaskForm):
    title = StringField('Title')
    only_campus = HiddenField('Only Campus')
    description = TextAreaField('Description')
    questions = HiddenField('Questions')
    term = HiddenField('Term')
    start_date = StringField('Start Date')
    end_date = StringField('End Date')
    start_time = StringField('Start Time')
    end_time = StringField('End Time')
    start_ampm = SelectField('Start AMPM', choices=[('AM', 'AM'), ('PM', 'PM')])
    end_ampm = SelectField('End AMPM', choices=[('AM', 'AM'), ('PM', 'PM')])
    day = HiddenField('Day')
    wage = HiddenField('Wage')
    every = SelectField('Every', choices=[("HOUR", "Hour"),("DAY", "Day"),("WEEK", "Week"),("MONTH", "Month"),("ONE TIME", "One Time")])
    tags = HiddenField('Tags')
    submit = SubmitField('Edit')


class JobForm(FlaskForm):
    answers = HiddenField('Answers')
    submit = SubmitField('Apply')


if __name__ == '__main__':
    app.run(debug=True)

