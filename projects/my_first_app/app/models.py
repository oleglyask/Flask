import imp
from tabnanny import check
from . import db
from werkzeug.security import generate_password_hash, check_password_hash


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
    password_hash = db.Column(db.String(128))

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

