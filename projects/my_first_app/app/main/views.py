from flask import redirect, render_template, session, flash, url_for, current_app, request
from flask_login import current_user, login_required

from .forms import CompositionForm, EditProfileForm, AdminLevelEditProfileForm
from . import main
from .. import db
from ..models import Composition, User, Role
from ..decorators import admin_required, permission_required
from ..models import Permission

# Home page
#Social media content START
#will display composition submit for and all the compositions posted
@main.route('/', methods=['GET', 'POST'])
def index():
    form = CompositionForm()
    if current_user.can(Permission.PUBLISH) \
            and form.validate_on_submit():
        composition = Composition(
            release_type=form.release_type.data,
            title=form.title.data,
            description=form.description.data,
            artist=current_user._get_current_object())
        db.session.add(composition)
        db.session.commit()
        composition.generate_slug()
        return redirect(url_for('.index'))

    page = request.args.get('page', 1, type=int)
    pagination = Composition.query.order_by(Composition.timestamp.desc()).paginate(
            page,
            per_page=current_app.config['MY_APP_COMPS_PER_PAGE'],
            error_out=False)
    compositions = pagination.items
    return render_template(
        'index.html',
        form=form,
        compositions=compositions,
        pagination=pagination
    )

# Will render an individual post based on a slug(Model.Composition.slug)
@main.route('/composition/<slug>')
def composition(slug):
    composition = Composition.query.filter_by(slug=slug).first_or_404()
    return render_template('composition.html', compositions=[composition])
#Social media content END

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
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = Composition.query.order_by(Composition.timestamp.desc()).paginate(
            page,
            per_page=current_app.config['MY_APP_COMPS_PER_PAGE'],
            error_out=False)
    compositions = pagination.items
    return render_template('user.html', user=user, compositions=compositions, pagination=pagination)

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

# The requested user to follow, specified in the URL, is loaded and verified
# 1) to exist and 2) they are already being followed. Given those checks pass,
# the user is followed and the session is finally committed to the database.
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("That is not a valid user.")
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash("Looks like you are already following that user.")
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f"You are now following {username}")
    return redirect(url_for('.user', username=username))

# Will unfollow a user
@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("That is not a valid user.")
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash("Looks like you are not following that user.")
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f"You are not following {username}")
    return redirect(url_for('.user', username=username))

# will compile a list of dictionaries of the user's followers and the timestamp
@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("That is not a valid user.")
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page,
        per_page=current_app.config['MY_APP_FOLLOWERS_PER_PAGE'],
        error_out=False)
    # convert to only follower and timestamp
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html',
                           user=user,
                           title_text="Followers of",
                           endpoint='.followers',
                           pagination=pagination,
                           follows=follows)

# will compile a list of dictionaries of the who users follows and the timestamp
@main.route('/following/<username>')
def following(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("That is not a valid user.")
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.following.paginate(
        page,
        per_page=current_app.config['MY_APP_FOLLOWERS_PER_PAGE'],
        error_out=False)
    # convert to only  who the user follows and timestamp
    follows = [{'user': item.following, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html',
                           user=user,
                           title_text="Follows",
                           endpoint='.following',
                           pagination=pagination,
                           follows=follows)