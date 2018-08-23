from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
# Initialize extension with your app.
app.config['SECRET_KEY'] = '55500b7625c92cd318daa58fabc00e16'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

# mirror imports escape
from rpd_site import routes