
# import datetime
from datetime import datetime
import hashlib
import re
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import AnonymousUserMixin

# Values represting different permissions for the Role model
class Permission:
    FOLLOW = 1
    REVIEW = 2
    PUBLISH = 4
    MODERATE = 8
    ADMIN = 16

# Create table models
# role table model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    # establishes a one(Role) to many(User) relationship
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return f"<Role {self.name}>"

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    # Standardizes the insertion of the permission when starting with a fresh database
    @staticmethod
    def insert_roles():
        roles = {
            'User':             [Permission.FOLLOW,
                                 Permission.REVIEW,
                                 Permission.PUBLISH],
            'Moderator':        [Permission.FOLLOW,
                                 Permission.REVIEW,
                                 Permission.PUBLISH,
                                 Permission.MODERATE],
            'Administrator':    [Permission.FOLLOW,
                                 Permission.REVIEW,
                                 Permission.PUBLISH,
                                 Permission.MODERATE,
                                 Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            # see if role is already in table
            role = Role.query.filter_by(name=r).first()
            if role is None:
                # it's not so make a new one
                role = Role(name=r)
            role.reset_permissions()
            # add whichever permissions the role needs
            for perm in roles[r]:
                role.add_permission(perm)
            # if role is the default one, default is True
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

# Association table to link the followers and followed of the User table
# this will establish MANY to MANY relationship between the users (user follows many | user has many followers)
class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer,
                            db.ForeignKey('users.id'),
                            primary_key=True)
    following_id = db.Column(db.Integer,
                             db.ForeignKey('users.id'),
                             primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# users table model
# from UserMixin will inherit the following properties and get_id() function
# is_authenticated: Must be True if the user has valid login credentials and is currently logged in, otherwise False.
# is_active: Must be True if the user is allowed to log in or False if not. Basically it means that if an account is not disabled, is_active will return True.
# is_anonymous: This must always be False for regular users who login and is only True for any user that is not logged in
# get_id(): This function returns a unique identifer for user
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    bio = db.Column(db.Text())
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    #social media content start
    compositions = db.relationship('Composition', backref='artist', lazy='dynamic')
    following = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),#lazy='joined' will load all the objects from a single select query
                               lazy='dynamic',
                               cascade='all, delete-orphan') #will delete rows in Follow table(instead of setting to NULL) if user is deleted
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.following_id],
                                backref=db.backref('following', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    # The joined lazy mode causes any related Follow objects to be loaded immediately from the join query.
    # Say a user, George, has 10 followers. If you have George's User object as george, calling george.followers.all()
    # gives a list of 10 Follow instances. Each of those instances has the follower and following back reference attributes
    # set to the corresponding users. With joined, all this happens in a single database query.
    # You can get all of the information you need, the users that follow George, loaded and ready to go just
    # from the george.followers.all(). The default select lazy mode would instead require 11 total database queries!
    # Ten of them would be needed to query the individual users in each Follow instance.
    #social media content end

    # dynamic lazy mode: As for the second lazy argument on the User side, it is set to the dynamic lazy mode similar to the
    # relationship between Role and Users. The relationship attributes in this case return a query object so that additional
    # filters can be added, instead of just returning the items directly.

    # The cascade argument takes a comma-separated list of options. The all option represents all cascade options except delete-orphan.

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Assignes a role to the user. Default role is "user", if email matches Admin email, assigns admin role
        if self.role is None:
            if self.email == current_app.config['MY_APP_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        # Assigns a hash number to use to fethc the avatar picture
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.email_hash()

    def __repr__(self):
        return f"<User {self.username}>"

    # Will run if User.password attribute is attempted to be READ
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    # will return of compositions of users that the SELF user is following
    # Has not been tested or implemented in a view
    # Example of a join query on db
    # Returns Composition objects joined with Follow table
    @property
    def followed_compositions(self):
        return Composition.query.join(
            Follow, Follow.following_id == Composition.artist_id)\
            .filter(Follow.follower_id == self.id)

    # Will run if User.password attribute is attempted to be SET
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # returns true if the the password and the password_hash preresentation matches.
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Generate a confirmation token
    # Used to confirm an account via email
    def generate_confirmation_token(self, expiration_sec=3600):
        s = Serializer(current_app.secret_key, expiration_sec)
        return s.dumps({'confirm_id': self.id}).decode('utf-8')

    # Confirms that the tokens match
    # Checks that the token itself is valid,that the token hasn't expired, and that the data hidden within matches the user's ID
    def confirm(self, token):
        s = Serializer(current_app.secret_key)
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm_id') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    # returns if the user can perform a given (perm) operation
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    # checks if the user is administrator
    def is_administrator(self):
        return self.can(Permission.ADMIN)

    # will update the last seen column
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    # Returns a hash number based on the email address
    def email_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    # will return a url string to request a Unicorn profile picture from Unicornify.com
    def unicornify(self, size=128):
        url = 'https://unicornify.pictures/avatar'
        hash = self.avatar_hash or self.email_hash()
        return f'{url}/{hash}?s={size}'

    #Social media content START
    # helper function to set follow and unfollow of users

    # a new row is inserted in the follows table linking a user to the passed-in user
    # there is no db.session.commit().  It will be called in the view function
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, following=user)
            db.session.add(f)

    # will delete the row in follows table pertaining to the user that is to be unfollowed.
    # there is no db.session.commit().  It will be called in the view function
    def unfollow(self, user):
        f = self.following.filter_by(following_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        if user.id is None:
            return False
        return self.following.filter_by(
            following_id=user.id).first() is not None

    def is_a_follower(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(
            follower_id=user.id).first() is not None
    #Social media content END

#Social media content START
class ReleaseType:
    SINGLE = 1
    EXTENDED_PLAY = 2
    ALBUM = 3

    @staticmethod
    def releaseTypeName(releaseType):
        if releaseType == 1:
            return "Single"
        elif releaseType == 2:
            return "Extended Play"
        else:
            return "Album"

#Models a Music post that a user can make of their music
class Composition(db.Model):
    __tablename__ = 'compositions'
    id = db.Column(db.Integer, primary_key=True)
    release_type = db.Column(db.Integer)
    title = db.Column(db.String(64))
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    slug = db.Column(db.String(128), unique=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def generate_slug(self):
        self.slug = f"{self.id}-" + re.sub(r'[^\w]+', '-', self.title.lower())
        db.session.add(self)
        db.session.commit()
#Social media content END


# User before they have signed in or registered
class AnonymousUser(AnonymousUserMixin):
    def can(self, perm):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

# decorator function that will, given a user identifier, return a UserMixin that corresponds to that identifier.
# Put more simply in this case, this function needs to return a User with the id that matches what is passed in
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


