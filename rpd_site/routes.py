import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from rpd_site import app, db, bcrypt
from rpd_site.models import User, Post
from rpd_site.forms import RegistrationForm, LoginForm, UpdateAccountForm, UpdatePicture
from flask_login import login_user, current_user, logout_user, login_required

last_news_added = "26 Серпня 2020"

articles = [
    {'Author': 'Denys Tarnavskyi',
     'Title': 'Савосік Саня отримав премію на конференції юних вчених',
     'Date': '18, Aug, 2018',
     'Content': 'Nam liber tempor cum soluta nobis eleifend option congue nihil imperdiet doming id quod mazim placerat facer possim assum.' \
                ' Lorem ipsum dolor sit amet, consectetuer mpor cum soluta nobis eleifend option congue nihil imperdiet doming id quod mazim placerat facer possim assum.' \
                ' Lorem ipsum dolor sit amet, consectetuempor cum soluta nobis eleifend option congue nihil imperdiet doming id quod mazim placerat facer possim assum.' \
                ' Lorem ipsum dolor sit amet, consectetuempor cum soluta nobis eleifend option congue nihil imperdiet doming id quod mazim placerat facer possim assum.' \
                ' Lorem ipsum dolor sit amet, consectetuempor cum soluta nobis eleifend option congue nihil imperdiet doming id quod mazim placerat facer possim assum.' \
                ' Lorem ipsum dolor sit amet, consectetueadipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna ' \
                'aliquam erat volutpat. '},
    
    {'Author': 'Ihor Beh',
     'Title': 'Збочинці будуть покарані!',
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
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Ваш обліковий запис створено.', 'success')
        print("User: " + form.username.data + " , email: " + form.email.data + " registered")
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form, title="Реєстрація")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            print("User: " + str(user) + " logged in")
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Неправильний email або пароль!', 'danger')
    return render_template('login.html', form=form, title="Увійти")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/img', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdatePicture()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
            db.session.commit()
            flash('Фото оновлено', 'success')
            return redirect(url_for('account'))
        
    image_file = url_for('static', filename='img/' + current_user.image_file)
    return render_template('account.html', title='Обліковий запис', form=form, image_file=image_file)


