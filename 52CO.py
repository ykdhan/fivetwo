from flask import Flask, render_template, flash, redirect, url_for, request
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField, IntegerField, PasswordField, BooleanField, HiddenField, TextAreaField
from wtforms.validators import Email, Length, NumberRange, DataRequired, InputRequired, EqualTo, AnyOf, Regexp, Optional
from flask_wtf import FlaskForm, validators
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import datetime
from flask_babel import Babel, gettext, ngettext
from flask_mail import Mail, Message
import string, random
import re

import db


app = Flask(__name__)
mail = Mail(app)

app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.mail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'zero.defects@mail.com',
	MAIL_PASSWORD = 'Zerodefects1!'
)
app.config['SECRET_KEY'] = '52CO Key'
app.config['WTF_CSRF_ENABLED'] = False



# app that runs before each db connection.
@app.before_request
def before():
    db.open_db_connection()


# app that runs after each db connection.
@app.teardown_request
def after(exception):
    db.close_db_connection()





@app.route('/', methods=["GET", "POST"])
def index():
	jobs = db.jobs()
	print (jobs)
	return render_template('index.html', jobs=jobs)


class LoginForm(FlaskForm):
	username = StringField('Nombre de usuario', validators=[DataRequired()])
	password = PasswordField('Contraseña', validators=[DataRequired()])
	submit = SubmitField('Registrarse')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', form=form)


if __name__ == '__main__':
    app.run()

'''
# LOGIN
login_mgr = LoginManager(app)


# authenticates a user by taking their login and password and checking it against the user table.
def authenticate(username, password):
    for user in db.all_users():
        if username == user['username'] and password == user['password']:
            return username
    return None


# defines the user class which returns various values of the logged in user.
class User(object):
    def __init__(self, username):
        self.username = username
        self.name = db.username_to_name(username)
        self.id = db.username_to_id(username)
        self.role = db.find_user_role(self.id)['description']
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return self.username

    def __repr__(self):
        return "<Usario '{}' {} {} {}>".format(self.username, self.is_authenticated, self.is_active, self.is_anonymous)


# Flask-Login calls this function on every request to recreate the current user object
# based on the unique ID it stored previously the session object.
@login_mgr.user_loader
def load_user(id):
    return User(id)


# Defines the form used by the app to handle login information.
class LoginForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Registrarse')


# application file that handles the login page.
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if authenticate(username, password):
            # Credentials authenticated.
            user = User(username)
            login_user(user)
            flash(_('Logged in successfully as {}'.format(username)))
            return redirect(url_for('index'))
        else:
            # Authentication failed.
            flash(_('Invalid username or password'))
    return render_template('login.html', form=form)


# app that handles the logout functionality.
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('Logged out'))
    return redirect(url_for('index'))

'''


