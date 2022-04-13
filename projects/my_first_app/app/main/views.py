from flask import redirect, render_template, session, flash, url_for
from flask_login import current_user, login_required

from .forms import EditProfileForm, AdminLevelEditProfileForm
from . import main
from .. import db
from ..models import User, Role
from ..decorators import admin_required, permission_required
from ..models import Permission

# Home page
@main.route('/', methods=['GET', 'POST'])
def index():

    """    form = NameForm()
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
    # return render_template('index.html', form=form, name=session.get('name'), known=session.get('known', False)) """

    return render_template('index.html')


# route() comes first
# then check if user authenticated
# then check their permission
# The topmost decorators are "evaluated" before the others

@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return render_template('admin_only.html', users=User.query.all())


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def for_moderators_only():
    return "Greetings, moderator!"

# will get a user object and render the user.html object.  If no user found, then 404 page will be rendered
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

# will allow user to edit it's profile
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.bio = form.bio.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('You successfully updated your profile! Looks great.')
        return redirect(url_for('main.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.bio.data = current_user.bio
    return render_template('edit_profile.html', form=form)

# will allow Admin to edit anyone's profile
@main.route('/editprofile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_profile(id):
    user = User.query.filter_by(id=id).first()
    form = AdminLevelEditProfileForm(role=user.role_id, user=user) #will default to the user's current role
    if form.validate_on_submit():
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role_id = form.role.data
        user.name = form.name.data
        user.location = form.location.data
        user.bio = form.bio.data
        db.session.add(user)
        db.session.commit()
        flash('You successfully updated profile! Looks great.')
        return redirect(url_for('main.user', username=user.username))

    form.username.data = user.username
    form.confirmed.data = user.confirmed
    # form.role.choices = [(role.id, role.name) for role in Role.query.all()]
    form.name.data = user.name
    form.location.data = user.location
    form.bio.data = user.bio
    return render_template('edit_profile.html', form=form)
