from flask import render_template, url_for, flash, redirect, request, abort, send_file
from rpd_site import app, db, bcrypt, s, mail
from rpd_site.models import User, Post
from rpd_site.forms import RegistrationForm, LoginForm, UpdateAccountForm, UpdatePicture, PostForm
from flask_login import login_user, current_user, logout_user, login_required
from termcolor import colored
from itsdangerous import SignatureExpired
from flask_mail import Message
from rpd_site.helpers import password_check, save_picture
from rpd_site.constants import *
from smtplib import SMTPException


@app.route('/index')
@app.route('/')
def index():
	month_translation = {'January': 'Cічня', 'February': 'Лотого', 'March': 'Березня',
						 'April': 'Квітня', 'May': 'Травня', 'June': 'Червня', 'July': 'Липня',
						 'August': 'Серпня', 'September': 'Вересня', 'October': 'Жовтня',
						 'November': 'Листопада', 'December': 'Грудня'}
	last_3_posts = Post.query.all()[-3:]
	if last_3_posts:
		# get date of the last post
		day = last_3_posts[-1].date_posted.strftime('%d')
		month = last_3_posts[-1].date_posted.strftime('%B')
		year = last_3_posts[-1].date_posted.strftime('%Y')
		time = last_3_posts[-1].date_posted.strftime('%X')
	# in case of 0 posts
	else:
		day = "26"
		month = "August"
		year = "1995"
		time = "08:54:14"
	return render_template('index.html', last_3_posts=last_3_posts, day=day, month=month_translation[month], year=year,
						   time=time)


@app.route('/news')
def news():
	# LIFO list
	posts = reversed(Post.query.all())
	return render_template('news.html', posts=posts, title="Новини")


@app.route('/history')
def history():
	return render_template('history.html', title="Історія")


@app.route('/schedule')
def schedule():
	return render_template('schedule.html', title="Розклад")


@app.route('/about')
def about():
	return render_template('news_old.html', articles=articles, title="Про Нас")


@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		flash('Ви вже ввійшли в аккаунт як ' + current_user.username, 'danger')
		return redirect(url_for('index'))
	else:
		form = RegistrationForm()
		if request.method == 'GET':
			return render_template('register.html', form=form, title="Реєстрація")
		elif request.method == 'POST':
			# check password weakness first
			if password_check(form.password.data):
				if form.validate_on_submit():
					# store only hash of the password
					hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
					user = User(username=form.username.data, email=form.email.data, password=hashed_password)
					email = request.form['email']
					# global unique confirmation link token
					global token
					token = s.dumps(email, salt=VAR_MAIL_SALT)
					msg = Message('confirm email', sender='marzique@gmail.com', recipients=[email])
					link = url_for('confirm_email', token=token)
					msg.body = 'Для того щоб підтвердити цю електронну адресу перейдіть за цим посиланням: ' \
							   + request.url_root[:-1] + link
					try:
						mail.send(msg)
						db.session.add(user)
						db.session.commit()
						flash('Ваш обліковий запис створено. Для підтвердження поштової адреси перейдіть по посиланню '
							  'яке було надіслано на адресу: ' + form.email.data, 'success')
						print()
						print(colored("User: " + form.username.data + " , email: " + form.email.data + " registered",
									  'blue'))
						print(colored("token: " + token, 'blue'))
						print()
						return redirect(url_for('login'))
					# catch GMAIL/SMTP error here
					except SMTPException:
						#  https://stackoverflow.com/a/16120288/10103803 - add logging here !!
						print(
							colored("User: " + form.username.data + " , email: " + form.email.data + " not registered",
									'red'))
						print(colored("SMTP error ", 'red'))
						flash('Щось пішло не так, спробуйте пізніше або зверніться до адміністратора!', 'danger')
			else:
				print(colored("User: " + form.username.data + " , email: " + form.email.data + " used weak password",
							  'red'))
				flash('Ваш пароль дуже слабкий, спробуйте додати Великі, малі літери, цифри, та спеціальні символи. '
					  'Пароль має складатись з щонайменше ' + str(VAR_MIN_PASS_LEN) + ' символів', 'danger')

			return render_template('register.html', form=form, title="Реєстрація")


@app.route('/confirm_email/<token>', methods=['GET', 'POST'])
def confirm_email(token):
	if current_user.is_authenticated:
		try:
			get_token = s.loads(token, salt=VAR_MAIL_SALT, max_age=VAR_TOKEN_MAX_AGE)
		except SignatureExpired:
			return '<h1>Старе посилання. Для підтвердження пошти зверніться до адміністратора.</h1><br> \
				   <a href="' + url_for("index") + '">Повернутись на сайт</a>'

		# confirm user
		current_user.confirmed = 1
		db.session.commit()
		flash("Пошта " + current_user.email + " прив'язана до аккаунту - " + current_user.username, 'success')
		return redirect(url_for('account'))
	else:
		flash("Спочатку авторизуйтесь!", 'danger')
		return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
	# how many times user tried to login
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	else:
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
				return redirect(url_for('login'))
	return render_template('login.html', form=form, title="Увійти")


@app.route('/logout')
def logout():
	print()
	print(colored("User: " + str(current_user.username) + " logged out", 'red'))
	print()
	logout_user()
	return redirect(url_for('login'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
	form = UpdatePicture()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data, VAR_AVATAR_SIZE, True)
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
		if form.picture.data:
			picture_file = save_picture(form.picture.data, VAR_POST_PIC_SIZE, False)
			post.image_file = picture_file
		db.session.add(post)
		db.session.commit()
		flash('Новину додано!', 'success')
		return redirect(url_for('news'))
	return render_template('new_post.html', title='Додати новину', form=form, legend='Додати новину')


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
		if form.picture.data:
			picture_file = save_picture(form.picture.data, VAR_POST_PIC_SIZE, False)
			post.image_file = picture_file
		post.title = form.title.data
		post.content = form.content.data
		db.session.commit()
		flash('Новину відредаговано', 'success')
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

@app.route('/account/update', methods=['GET', 'POST'])
def update_account():
	form = UpdateAccountForm()
	if current_user.is_authenticated:
		if request.method == 'POST':
				if form.validate_on_submit():
					# if user changing email address
					if current_user.email != form.email.data:
						global token
						token = s.dumps(form.email.data, salt=VAR_MAIL_SALT)
						msg = Message('confirm new email', sender='marzique@gmail.com', recipients=[form.email.data])
						link = url_for('confirm_email', token=token)
						msg.body = 'Для того щоб підтвердити цю електронну адресу перейдіть за цим посиланням: ' \
								   + request.url_root[:-1] + link
						try:
							mail.send(msg)
							current_user.username = form.username.data
							current_user.email = form.email.data
							current_user.confirmed = 0
							db.session.commit()
							flash('Обліковий запис успішно відредаговано. Для підтвердження поштової адреси перейдіть по посиланню '
								  'яке було надіслано на адресу: ' + form.email.data, 'success')
							print()
							print(colored("User new name: " + form.username.data + " , changed email to: " + form.email.data,
										  'blue'))
							print(colored("token: " + token, 'blue'))
							print()
							return redirect(url_for('account'))
						# catch GMAIL/SMTP error here
						except SMTPException:
							#  https://stackoverflow.com/a/16120288/10103803 - add logging here !!
							print(
								colored("User: " + form.username.data + " , email: " + form.email.data + " didn't change account",
										'red'))
							print(colored("SMTP error ", 'red'))
							flash('Щось пішло не так, спробуйте пізніше або зверніться до адміністратора!', 'danger')
					# just change username
					else:
						current_user.username = form.username.data
						db.session.commit()
						flash(
							'Обліковий запис успішно відредаговано.', 'success')
						print()
						print(
							colored("User new name: " + form.username.data + " , old email : " + form.email.data,
									'blue'))
						print()
						return redirect(url_for('account'))

		elif request.method == 'GET':
			return render_template('update_account.html', title='Редагувати профіль',
								   form=form, legend='Редагувати профіль')

	else:
		flash("Увійдіть у свій обліковий запис", 'danger')
		return redirect(url_for('login'))

	return render_template('update_account.html', title='Редагувати профіль',
						   form=form, legend='Редагувати профіль')
