from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from termcolor import colored
from rpd_site.constants import VAR_APP_SECRET_KEY, VAR_DEBUG, VAR_CFG_FILE
import os

app = Flask(__name__)

# check if heroku env
on_heroku = False
if 'IS_HEROKU' in os.environ:
	on_heroku = True
	# create empty cfg file in cwd
	dir_path = os.path.dirname(os.path.realpath(__file__))
	f = open(os.path.join(dir_path, 'config.cfg'), 'w')
	f.close()
	app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
	app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
else:
	print(colored('LOADED DEVELOPMENT SETTINGS', 'green'))

# Initialize extension with your app.
app.config.from_pyfile(VAR_CFG_FILE)
app.config['SECRET_KEY'] = VAR_APP_SECRET_KEY
app.config['DEBUG'] = VAR_DEBUG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LcPZ3UUAAAAAO_WGbcXUI9tsI-Ya8Sq89mePlAW'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LcPZ3UUAAAAAFN3SdsrsEAk9xsslHQHW_byLYmg'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# recaptcha disable for offline/development
RECAPTCHA_DISABLE = True





mail = Mail(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# prevents CSRF (?)
login_manager.session_protection = "strong"

# mirror imports escape
from rpd_site import routes
