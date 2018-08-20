from flask import Flask, render_template, url_for
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '55500b7625c92cd318daa58fabc00e16'

last_news_added = "99 Серпня 2020"

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

@app.route('/about')
def about():
    return render_template('news.html', articles=articles, title="Про Нас")

@app.route('/register')
def register():
    form = RegistrationForm()
    return render_template('register.html', form=form, title="Реєстрація")

@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', form=form, title="Увійти")


if __name__ == '__main__':

    app.run(debug=True)
