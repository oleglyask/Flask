
from pickle import FALSE
from flask_bootstrap import Bootstrap
from flask import Flask, redirect, render_template, abort, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# create a Form class called NameForm that extends the FlaskForm class
class NameForm(FlaskForm):
    name = StringField("Enter your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")
# birthday form
class BirthdayForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    birthday = DateField('Birthday', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Get absolute path of the directory where app.py file is located
basedir = os.path.abspath(os.path.dirname(__file__))

# Initialize Flask app
app = Flask(__name__)
# Initialize variables that sqlite will use
app.config['SECRET_KEY'] = '12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database object
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True) #render_as_batch is for sqlite only

# Create table models
# role table model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return f"<Role {self.name}>"

# users table model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return f"<User {self.username}>"

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

# Initialize Bootstrap by passing a Flask instance to it in the constructor
bootstrap = Bootstrap(app)

# Home page
@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    # if form has been submitted. This will get called only on  'POST' requests with successful validate
    if form.validate_on_submit():
        name_entered = form.name.data
        user = User.query.filter_by(username=name_entered).first()
        # if user doesn't exist yet, create one and set session[known] to False
        if user == None:
            role_id = Role.query.filter_by(name='User').first().id
            user = User(username=name_entered, role_id=role_id)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        # if user exists then session[known] is True
        else:
            session['known'] = True

        # rememmber what was typed into the form with session
        session['name'] = name_entered
        # shows up as a message to the user
        flash('Good Job')
        # call the index() again but as a "GET" so if user refreshes, it will refresh with "GET" and NOT 'POST'
        return redirect(url_for('index'))
    # this will get called only on GET requests
    return render_template('index.html', form=form, name=session.get('name'), known=session.get('known', FALSE))

# route that will render a form to input birthday and will flash a zodiac sign based on the birthday
@app.route('/zodiac', methods=['GET', 'POST'])
def zodiac():
    form = BirthdayForm()
    if form.validate_on_submit():
        flash('Aries')
        return redirect(url_for('index'))
    return render_template('zodiac.html', form=form)


# username variable will populated from url '<username>' when the user navigates to localhost/user/oleg
@app.route('/user/<user_id>')
def user_with_arg(user_id):
    username = load_user(int(user_id))
    if not username:
        abort(404)
    return render_template('user.html', username=username)

# /user route with no user argument passed in
@app.route('/user')
def user_no_arg():
    return render_template('user.html')

# error handlers
@app.errorhandler(403)
def forbidden(e):
    error_title = "Forbidden"
    error_msg = "You shouldn't be here!"
    return render_template('error.html',
                           error_title=error_title,
                           error_msg=error_msg), 403

@app.errorhandler(404)
def page_not_found(e):
    error_title = "Not Found"
    error_msg = "That page doesn't exist"
    return render_template('error.html',
                           error_title=error_title,
                           error_msg=error_msg), 404


@app.errorhandler(500)
def internal_server_error(e):
    error_title = "Internal Server Error"
    error_msg = "Sorry, we seem to be experiencing some technical difficulties"
    return render_template('error.html',
                           error_title=error_title,
                           error_msg=error_msg), 500

def load_user(user_id):
    if user_id == 1:
        return "Oleg"
    elif user_id == 2:
        return "Elena"
    else:
        return None
