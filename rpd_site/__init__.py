from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from rpd_site.constants import VAR_SAFE_TIMED_KEY

from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer
from rpd_site.constants import VAR_APP_SECRET_KEY, VAR_DEBUG, VAR_CFG_FILE

app = Flask(__name__)

# Initialize extension with your app.
app.config.from_pyfile(VAR_CFG_FILE)
app.config['SECRET_KEY'] = VAR_APP_SECRET_KEY
app.config['DEBUG'] = VAR_DEBUG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LcPZ3UUAAAAAO_WGbcXUI9tsI-Ya8Sq89mePlAW'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LcPZ3UUAAAAAFN3SdsrsEAk9xsslHQHW_byLYmg'

mail = Mail(app)

# mail secret
s = URLSafeTimedSerializer(VAR_SAFE_TIMED_KEY)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# mirror imports escape
from rpd_site import routes
