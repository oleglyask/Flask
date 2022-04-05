
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

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

    def __repr__(self):
        return f"<User {self.username}>"

    # Will run if User.password attribute is attempted to be READ
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

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

# decorator function that will, given a user identifier, return a UserMixin that corresponds to that identifier.
# Put more simply in your case, this function needs to return a User with the id that matches what is passed in
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
