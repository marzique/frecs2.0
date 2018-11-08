from datetime import datetime
from rpd_site import db, login_manager
from flask_login import UserMixin
from flask_security import RoleMixin


# TODO comment here!
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# M2M association table between User and Role
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class User(db.Model, UserMixin):
    '''
    Main site account table
    '''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=0)
    posts = db.relationship('Post', backref='author', lazy=True)

    # user can have multiple roles
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='joined'))

    def add_role(self, role_name):
        role_search = Role.query.filter_by(name=role_name).first()
        if role_search:
            self.roles.append(role_search)
            db.session.commit()
        else:
            print(role_name + " doesn't exist!")
            return False

    def delete_role(self, role_name):
        role = Role.query.filter_by(name=role_name).first()
        if role:
            role.users.remove(self)
            db.session.commit()
        else:
            print(self.username + " doesn't have role " + role_name)
            return False

    def all_roles(self):
        roles = []
        for role in self.roles:
            roles.append(role.name)
        return roles

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.confirmed}')"


class Role(db.Model, RoleMixin):
    '''
    Multiple users can have the same role
    '''
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __str__(self):
        return self.name


class Post(db.Model):
    '''
    Posts table
    '''
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    # current local time instead of .utcnow
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default_post.png')

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}', '{self.content[:15]}')"
