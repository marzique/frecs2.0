import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from rpd_site import app, db, bcrypt
from rpd_site.models import User, Post
from rpd_site.forms import RegistrationForm, LoginForm, UpdateAccountForm, UpdatePicture, PostForm
from flask_login import login_user, current_user, logout_user, login_required
from termcolor import colored



@app.route('/index')
@app.route('/')
def index():
    month_translation = {'January': 'Cічня', 'February': 'Лотого', 'March': 'Березня',
                         'April': 'Квітня', 'May': 'Травня', 'June': 'Червня', 'July': 'Липня',
                        'August': 'Серпня', 'September': 'Вересня', 'October': 'Жовтня',
                         'November': 'Листопада', 'December': 'Грудня'}
    last_3_posts = Post.query.all()[-3:]
    day = last_3_posts[-1].date_posted.strftime('%d')
    month = last_3_posts[-1].date_posted.strftime('%B')
    year = last_3_posts[-1].date_posted.strftime('%Y')
    time = last_3_posts[-1].date_posted.strftime('%X')

    return render_template('index.html', last_3_posts=last_3_posts, day=day, month=month_translation[month], year=year, time=time)


@app.route('/index2')
def index2():
    return render_template('index2.html')


@app.route('/news')
def news():
    # LIFO list
    posts = reversed(Post.query.all())
    return render_template('news.html', posts=posts, title="Новини")


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
        # store only hash of the password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Ваш обліковий запис створено.', 'success')
        print()
        print(colored("User: " + form.username.data + " , email: " + form.email.data + " registered", 'blue'))
        print()
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
            print()
            print(colored(str(user) + " logged in", 'green'))
            print()
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Неправильний email або пароль!', 'danger')
    return render_template('login.html', form=form, title="Увійти")

@app.route('/logout')
def logout():
    print()
    print(colored("User: " + str(current_user.username) + " logged out", 'red'))
    print()
    logout_user()
    return redirect(url_for('login'))

def save_picture(form_picture):
    '''uploads square-cropped image with randomised
    filename and returns it's filename'''
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/img/avatars', picture_fn)
    output_size = (150, 150)
    i = Image.open(form_picture)
    # crop top square to leave aspect ratio
    f_width, _ = i.size
    i = i.crop((0,0,f_width,f_width))
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
        
    image_file = url_for('static', filename='img/avatars/' + current_user.image_file)
    return render_template('account.html', title='Обліковий запис', form=form, image_file=image_file)

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Новину додано', 'success')
        return redirect(url_for('news'))
    return render_template('new_post.html', title='Додати новину', form=form, legend='Нова новина')

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('new_post.html', title='Редагувати новину',
                           form=form, legend='Редагувати новину')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Видалено', 'success')
    return redirect(url_for('news'))
