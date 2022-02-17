from flask import redirect, render_template, session, flash, url_for
from . import main
from .. import db
from .forms import NameForm
from ..models import User, Role

# Home page
@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    # if form has been submitted. This will get called only on  'POST' requests with successful validate
    if form.validate_on_submit():
        name_entered = form.name.data
        user = User.query.filter_by(username=name_entered).first()
        # if user doesn't exist yet, create one and set session[known] to False
        if user == None:
            role_id = Role.query.filter_by(name='user').first().id
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
        return redirect(url_for('main.index'))
    # this will get called only on GET requests
    return render_template('index.html', form=form, name=session.get('name'), known=session.get('known', False))