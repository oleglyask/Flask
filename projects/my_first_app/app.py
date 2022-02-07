
from flask_bootstrap import Bootstrap
from flask import Flask, render_template
import os

# Initialize Flask app
app = Flask(__name__)
# Initialize Bootstrap by passing a Flask instance to it in the constructor
bootstrap = Bootstrap(app)

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# username variable will populated from url '<username>' when the user navigates to localhost/user/oleg
@app.route('/user/<username>')
def user_with_arg(username):
    return render_template('user.html', username=username)

# /user route with no user argument passed in
@app.route('/user')
def user_no_arg():
    return render_template('user.html')
