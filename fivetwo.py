from flask import Flask, render_template, flash, redirect, url_for, request, session
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField, IntegerField, PasswordField, BooleanField, HiddenField, TextAreaField
from wtforms.validators import Email, Length, NumberRange, DataRequired, InputRequired, EqualTo, AnyOf, Regexp, Optional
from flask_wtf import FlaskForm, validators
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import datetime
from flask_mail import Mail, Message
import string, random
import re
from flask_cas import CAS
from flask_cas import login
from flask_cas import logout

import db

app = Flask(__name__)
mail = Mail(app)

cas = CAS(app, '/cas')
app.config['CAS_SERVER'] = 'https://sso.taylor.edu/'
app.config['CAS_AFTER_LOGIN'] = 'cas'


app.config.update(
    DEBUG=True,
    # EMAIL SETTINGS
    MAIL_SERVER='smtp.mail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='fivetwo@mail.com',
    MAIL_PASSWORD='Five&Two52'
)
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
        if user['is_campus'] == 'NO' and email == user['email'] and password == user['password']:
            return email
    return None


# defines the user class which returns various values of the logged in user.
class User(object):
    def __init__(self, email):
        self.email = email
        self.name = db.user_info(email)['name']
        self.id = db.user_info(email)['id']
        self.is_registered = db.user_info(email)['is_registered']
        self.is_campus = db.user_info(email)['is_campus']
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
    login_form = LoginForm()
    signup_form = SignUpForm()

    if login_form.is_submitted():
        email = login_form.email.data
        password = login_form.password.data
        if authenticate(email, password):
            # Credentials authenticated.
            user = User(email)
            login_user(user)
            return redirect(url_for('index'))
        #else:
            #flash('Invalid username or password')
    if signup_form.validate_on_submit():
        if signup_form.password.data == signup_form.cpassword.data:
            rowcount = db.sign_up(signup_form.name.data, signup_form.email.data, signup_form.password.data, 'NO')
            if rowcount == 1:
                if authenticate(signup_form.email.data, signup_form.password.data):
                    user = User(email)
                    login_user(user)
                    return redirect(url_for('index'))
            else:
                flash("Error: Cannot post new job.")
        else:
            flash("Error: Confirm password.")
    return render_template('login.html', login_form=login_form, signup_form=signup_form, login=True)


# app that handles the logout functionality.
@app.route('/logout')
@login_required
def logout():
    if current_user.is_campus == 'YES':
        logout_user()
        return redirect('/cas/logout')
    else:
        logout_user()
        return redirect(url_for('index'))


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

    jobs = db.jobs()
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
            job['start_date'] = start_month+" "+str(start_day)+", "+start_year
            job['end_date'] = end_month+" "+str(end_day)+", "+end_year

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
    return render_template('index.html', jobs=outputs)


@app.route('/job/<job_id>', methods=["GET", "POST"])
def job(job_id):
    today = datetime.datetime.today()

    j = db.job(job_id)

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
        job['start_date'] = start_month + " " + str(start_day) + ", " + start_year
        job['end_date'] = end_month + " " + str(end_day) + ", " + end_year

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

    tags = db.job_tags(job_id)
    questions = db.job_questions(job_id)

    job['tags'] = tags
    job['questions'] = questions

    job_form = JobForm()

    if job_form.validate_on_submit():
        answers = []
        if job_form.answer1.data is not None and job_form.answer1.data != "":
            answers.append(job_form.answer1.data)
        if job_form.answer2.data is not None and job_form.answer2.data != "":
            answers.append(job_form.answer2.data)
        if job_form.answer3.data is not None and job_form.answer3.data != "":
            answers.append(job_form.answer3.data)

        rowcount = db.apply_job(current_user.id, job_id, answers)

        if rowcount == 1:
            return redirect(url_for('applications'))
        else:
            flash("Error: Cannot apply.")

    return render_template('job.html', job=job, form=job_form, today=today)


@app.route('/new', methods=["GET", "POST"])
def new():

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
        print('Term:'+str(post_form.term.data))

        if post_form.term.data == 'LONG':
            start_date = None
            end_date = None
        else:
            start_date = datetime.datetime.strptime(post_form.start_date.data, '%m/%d/%Y').strftime("%Y-%m-%d")
            end_date = datetime.datetime.strptime(post_form.end_date.data, '%m/%d/%Y').strftime("%Y-%m-%d")

        tags = post_form.tags.data.split("#")
        questions = []

        if post_form.question1.data is not None and post_form.question1.data != "":
            questions.append(post_form.question1.data)
        if post_form.question2.data is not None and post_form.question2.data != "":
            questions.append(post_form.question2.data)
        if post_form.question3.data is not None and post_form.question3.data != "":
            questions.append(post_form.question3.data)

        rowcount = db.post_job(current_user.id, post_form.title.data, post_form.description.data, post_form.term.data, start_date,
                           end_date, post_form.start_time.data, post_form.end_time.data, post_form.day.data,
                           int(post_form.wage.data), post_form.every.data, tags, questions)
        if rowcount == 1:
            return redirect(url_for('index'))
        else:
            flash("Error: Cannot post new job.")

    return render_template('new.html', form=post_form)


@app.route('/posts', methods=["GET", "POST"])
def posts():
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
            job['start_date'] = start_month + " " + str(start_day) + ", " + start_year
            job['end_date'] = end_month + " " + str(end_day) + ", " + end_year


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
        job['num_applications'] = len(db.job_applications(j['id']))
        outputs.append(job)
    return render_template('posts.html', jobs=outputs)


@app.route('/applications', methods=["GET", "POST"])
def applications():
    applications = db.applications(current_user.id)

    outputs = []
    for a in applications:
        apply = {}
        j = db.job(a['job_id'])
        job = {}
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
            job['start_date'] = start_month + " " + str(start_day) + ", " + start_year
            job['end_date'] = end_month + " " + str(end_day) + ", " + end_year

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

        tags = db.job_tags(j['id'])

        job['tags'] = tags

        questions = []
        num = 0
        for i in db.job_questions(j['id']):
            q = {}
            q['question'] = i['question']
            q['answer'] = db.job_answers(j['id'])[num]['answer']
            questions.append(q)
            num += 1
        apply['questions'] = db.job_questions(j['id'])
        apply['job'] = job
        apply['date'] = datetime.datetime.strptime(a['created_at'], '%Y-%m-%d %H:%M:%S').strftime("%b %d, %Y")

        outputs.append(apply)

    return render_template('applications.html', applications=outputs)


@app.route('/sign-up', methods=["GET", "POST"])
def sign_up():
    user = db.user(current_user.id)
    if db.user(current_user.id) is None:
        return redirect(url_for('index'))
    if user['is_campus'] == 'YES':
        signup_form = SignUpMoreFormCampus()
        signup_form.name.data = current_user.name
        is_campus = True
        if user['is_student'] == 'YES':
            is_student = True
        else:
            is_student = False
    else:
        signup_form = SignUpMoreForm()
        is_campus = False
        is_student = False

    if signup_form.is_submitted():
        if is_campus:
            if is_student:
                rowcount = db.sign_up_more(current_user.id, signup_form.name.data, signup_form.gender.data, signup_form.contact.data,
                                           signup_form.birth.data, signup_form.major.data, signup_form.year.data, None, None)
            else:
                rowcount = db.sign_up_more(current_user.id, signup_form.name.data, signup_form.gender.data, signup_form.contact.data,
                                           signup_form.birth.data, None, None, signup_form.department.data,
                                           signup_form.position.data)
        else:
            rowcount = db.sign_up_more(current_user.id, None, signup_form.gender.data, signup_form.contact.data, signup_form.birth.data,
                                       None, None, None, None)
        if rowcount == 1:
            return redirect(url_for('index'))
        else:
            flash("Error: Cannot sign up.")

    return render_template('sign-up.html', signup_form=signup_form, is_campus=is_campus, is_student=is_student)


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    login_submit = SubmitField('Sign In')


class SignUpForm(FlaskForm):
    name = StringField('Name')
    email = StringField('Email Address')
    password = PasswordField('Password')
    cpassword = PasswordField('Confirm Password')
    signup_submit = SubmitField('Sign Up')


class SignUpMoreForm(FlaskForm):
    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female')])
    contact = StringField('Email Address')
    birth = StringField('Email Address')
    signup_submit = SubmitField('Sign Up')


class SignUpMoreFormCampus(FlaskForm):
    name = StringField('Name')
    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female')])
    contact = StringField('Email Address')
    birth = StringField('Email Address')
    major = StringField('Major')
    year = SelectField('Class Year', choices=[('Freshman', 'Freshman'), ('Sophomore', 'Sophomore'), ('Junior', 'Junior'), ('Senior', 'Senior')])
    department = StringField('Department')
    position = StringField('Position')
    signup_submit = SubmitField('Sign Up')


class PostForm(FlaskForm):
    title = StringField('Title')
    description = TextAreaField('Description')
    question1 = StringField('Question 1')
    question2 = StringField('Question 2')
    question3 = StringField('Question 3')
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


class JobForm(FlaskForm):
    answer1 = HiddenField('Answer 1')
    answer2 = HiddenField('Answer 2')
    answer3 = HiddenField('Answer 3')
    submit = SubmitField('Apply')


if __name__ == '__main__':
    app.run(debug=True)

