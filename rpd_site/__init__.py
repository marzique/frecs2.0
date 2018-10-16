from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialize extension with your app.
app.config.from_pyfile('config.cfg')
app.config['SECRET_KEY'] = '55500b7625c92cd318daa58fabc00e16'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

mail = Mail(app)

# mail secret
s = URLSafeTimedSerializer('testingkey')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# mirror imports escape
from rpd_site import routes
