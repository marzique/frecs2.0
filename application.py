from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Initialize extension with your app.
app.config['SECRET_KEY'] = '55500b7625c92cd318daa58fabc00e16'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
last_news_added = "99 Серпня 2020"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
	
	
articles = [
	{'Author': 'Denys Tarnavskyi',
	 'Title': 'Title Post1',
	 'Date': '18, Aug, 2018',
	 'Content': 'Nam liber tempor cum soluta nobis eleifend option congue nihil imperdiet doming id quod mazim placerat facer possim assum.' \
	            ' Lorem ipsum dolor sit amet, consectetuer mpor cum soluta nobis eleifend option congue nihil imperdiet doming id quod mazim placerat facer possim assum.' \
	            ' Lorem ipsum dolor sit amet, consectetuempor cum soluta nobis eleifend option congue nihil imperdiet doming id quod mazim placerat facer possim assum.' \
	            ' Lorem ipsum dolor sit amet, consectetuempor cum soluta nobis eleifend option congue nihil imperdiet doming id quod mazim placerat facer possim assum.' \
	            ' Lorem ipsum dolor sit amet, consectetuempor cum soluta nobis eleifend option congue nihil imperdiet doming id quod mazim placerat facer possim assum.' \
	            ' Lorem ipsum dolor sit amet, consectetueadipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna ' \
	            'aliquam erat volutpat. '},
	
	{'Author': 'Ihor Beh',
	 'Title': 'Title Post2',
	 'Date': '15, Aug, 2018',
	 'Content': 'Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis.'
	 }
]


@app.route('/index')
@app.route('/')
def index():
	return render_template('index.html', last_news_added=last_news_added)


@app.route('/index2')
def index2():
	return render_template('index2.html')


@app.route('/news')
def news():
	return render_template('news.html', articles=articles, title="Новини")

@app.route('/history')
def history():
	return render_template('history.html', title="Історія")


@app.route('/about')
def about():
	return render_template('news_old.html', articles=articles, title="Про Нас")


@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		flash(f'Обліковий запис створено', 'success')
		return redirect(url_for('login'))
	
	return render_template('register.html', form=form, title="Реєстрація")


@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		if form.email.data == 'marzique@gmail.com' and form.password.data == '1':
			flash('Успішно!', 'success')
			return redirect(url_for('index'))
		else:
			flash('Неправильний логін або пароль!', 'danger')
	return render_template('login.html', form=form, title="Увійти")


if __name__ == '__main__':
	app.run(debug=True)
