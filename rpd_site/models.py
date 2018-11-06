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
	image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
	password = db.Column(db.String(60), nullable=False)
	confirmed = db.Column(db.Boolean, nullable=False, default=0)
	posts = db.relationship('Post', backref='author', lazy=True)
	
	# user can have multiple roles
	roles = db.relationship('Role', secondary=roles_users,
							backref=db.backref('users', lazy='joined'))

	def add_role(self, role_name):
		role = Role(name=role_name)
		self.roles.append(role)
		db.session.commit()

	def delete_role(self, role_name):
		role = Role(name=role_name)
		self.roles.remove(role)
		db.session.commit()


	def __repr__(self):
		return f"User('{self.username}', '{self.email}', '{self.confirmed}')"


class Post(db.Model):
	'''
	Posts table
	'''
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)  # current local time instead of .utcnow
	content = db.Column(db.Text, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	image_file = db.Column(db.String(20), nullable=False, default='default_post.png')

	def __repr__(self):
		return f"Post('{self.title}', '{self.date_posted}', '{self.content[:15]}')"


class Role(db.Model, RoleMixin):
	'''
	Multiple users can have the same role
	'''
	__tablename__ = 'role'
	id = db.Column(db.Integer(), primary_key=True)
	name = db.Column(db.String(50), unique=True)

	def __str__(self):
		return self.name


