from flask import render_template, url_for, flash, redirect, request, abort, send_file
from rpd_site import app, db, bcrypt, mail
from .models import User, Post
from .forms import (RegistrationForm, LoginForm, UpdateAccountForm,
							UpdatePicture, PostForm, ResetRequest, ResetPassword)
from flask_login import login_user, current_user, logout_user, login_required, fresh_login_required
from termcolor import colored
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_mail import Message
from .helpers import password_check, save_picture, generate_confirmation_token, generate_password_token
from .constants import *
from smtplib import SMTPException
import os


@app.route('/index')
@app.route('/')
def index():
	# better than include other modules just for month translation
	month_translation = {'January': 'Cічня', 'February': 'Лотого', 'March': 'Березня',
						 'April': 'Квітня', 'May': 'Травня', 'June': 'Червня', 'July': 'Липня',
						 'August': 'Серпня', 'September': 'Вересня', 'October': 'Жовтня',
						 'November': 'Листопада', 'December': 'Грудня'}
	last_3_posts = Post.query.all()[-3:]
	# at least 1 post exists
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
		time = "00:00:01"
	return render_template('index.html', last_3_posts=last_3_posts, day=day, month=month_translation[month], year=year,
							time=time, menuitem="index")


@app.route('/news')
def news():
	# check id injection here!
	page = request.args.get('page', 1, type=int)
	# LIFO
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=VAR_POST_PER_PAGE)
	return render_template('news.html', posts=posts, title="Новини", menuitem='news')


@app.route('/history')
def history():
	return render_template('history.html', title="Історія", menuitem='history')


@app.route('/schedule')
def schedule():
	return render_template('schedule.html', title="Розклад", menuitem='schedule')


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
			if form.validate_on_submit():
				# check password weakness first
				if password_check(form.password.data):
					# store only hash of the password
					hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

					# email is not case sensitive
					email = form.email.data.lower()
					user = User(username=form.username.data, email=email, password=hashed_password)
					token = generate_confirmation_token(email)
					msg = Message('Підтвердження скриньки', sender='marzique@gmail.com', recipients=[email])
					confirm_url = url_for('confirm_email', token=token, _external=True)
					msg.html = render_template('emails/confirmation_email.html', full_link=confirm_url)
					try:
						mail.send(msg)
						db.session.add(user)
						db.session.commit()
						flash('Ваш обліковий запис створено. Для підтвердження поштової адреси перейдіть по посиланню '
							  'яке було надіслано на адресу: ' + email, 'success')
						# change it to logging
						print()
						print(colored("User: " + form.username.data + " , email: " + email + " registered",
									  'blue'))
						print(colored("token: " + token, 'blue'))
						print()
						login_user(user)
						return redirect(url_for('account'))
					# catch GMAIL/SMTP error here
					except SMTPException:
						#  https://stackoverflow.com/a/16120288/10103803 - add logging here !!
						print(
							colored("User: " + form.username.data + " , email: " + email + " not registered",
									'red'))
						print(colored("SMTP error ", 'red'))
						flash('Щось пішло не так, спробуйте пізніше або зверніться до адміністратора!', 'danger')
				else:
					print(
						colored("User: " + form.username.data + " , email: " + form.email.data.lower() + " used weak password",
								'red'))
					flash(
						'Ваш пароль дуже слабкий, спробуйте додати Великі, малі літери, цифри, та спеціальні символи. '
						'Пароль має складатись з щонайменше ' + str(VAR_MIN_PASS_LEN) + ' символів', 'danger')

			return render_template('register.html', form=form, title="Реєстрація")


@app.route('/confirm_email/<token>', methods=['GET', 'POST'])
def confirm_email(token):
	if current_user.is_authenticated:
		try:
			signature = URLSafeTimedSerializer(VAR_SAFE_TIMED_KEY)
			# check if URL correct and still valid
			signature.loads(token, salt=VAR_MAIL_SALT + current_user.email, max_age=VAR_TOKEN_MAX_AGE)
		except SignatureExpired:
			return '<h1>Старе посилання. Для підтвердження пошти зверніться до адміністратора.</h1><br> \
				   <a href="' + url_for("index") + '">Повернутись на сайт</a>'

		except BadSignature:
			return '<h1>Посилання не є дійсним. Для підтвердження пошти перейдіть по посиланню надісланому вам на пошту \
					або зверніться до адміністратора.</h1><br> \
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
			user = User.query.filter_by(email=form.email.data.lower()).first()
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
	file_to_delete = os.path.join(app.root_path, 'static/img/avatars', current_user.image_file)
	print(file_to_delete)
	if form.validate_on_submit():
		# update profile picture + delete previous
		if form.picture.data:
			picture_file = save_picture(form.picture.data, VAR_AVATAR_SIZE, True)
			current_user.image_file = picture_file
			db.session.commit()
			os.remove(file_to_delete)
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
@fresh_login_required
def update_account():
	form = UpdateAccountForm()
	if current_user.is_authenticated:
		if request.method == 'POST':
			if form.validate_on_submit():
				email = form.email.data.lower()
				# user changing email address
				if current_user.email != email:
					token = generate_confirmation_token(email)
					msg = Message('confirm new email', sender='marzique@gmail.com', recipients=[email])
					confirm_url = url_for('confirm_email', token=token, _external=True)
					msg.html = render_template('emails/confirmation_email_change.html', full_link=confirm_url)
					try:
						mail.send(msg)
						current_user.username = form.username.data
						current_user.email = email
						current_user.confirmed = 0
						db.session.commit()
						flash('Обліковий запис успішно відредаговано. Для підтвердження поштової адреси перейдіть по посиланню \
								яке було надіслано на адресу: ' + email, 'success')
						print()
						print(
							colored("User new name: " + form.username.data + " , changed email to: " + email,
									'blue'))
						print(colored("token: " + token, 'blue'))
						print()
						return redirect(url_for('account'))
					# catch GMAIL/SMTP error here
					except SMTPException:
						#  https://stackoverflow.com/a/16120288/10103803 - add logging here !!
						print(
							colored(
								"User: " + form.username.data + " , email: " + email + " didn't change account", 'red'))
						print(colored("SMTP error ", 'red'))
						flash('Щось пішло не так, спробуйте пізніше або зверніться до адміністратора!', 'danger')

				# user provided same email and username
				elif current_user.username == form.username.data and current_user.email == email:
					flash('Ви ввели старе ім\'я та адресу, змініть хоча б шось одне з двох!', 'danger')
				# just change username
				else:
					current_user.username = form.username.data
					db.session.commit()
					flash('Обліковий запис успішно відредаговано.', 'success')
					print()
					print(colored("User new name: " + form.username.data + " , old email : " + email, 'blue'))
					print()
					return redirect(url_for('account'))

		elif request.method == 'GET':
			return render_template('update_account.html', title='Редагувати профіль', form=form, legend='Редагувати профіль')

	else:
		flash("Спочатку увійдіть у свій обліковий запис", 'danger')
		return redirect(url_for('login'))

	return render_template('update_account.html', title='Редагувати профіль', form=form, legend='Редагувати профіль')


@app.route('/users', methods=['GET'])
def users():
	if current_user.is_authenticated:
		users = User.query.all()
		return render_template('users.html', users=users, title="Користувачі")

	else:
		flash("Спочатку увійдіть у свій обліковий запис", 'danger')
		return redirect(url_for('login'))


@app.route('/users/<int:user_id>', methods=['GET', 'POST'])
def user_id(user_id):
	if current_user.is_authenticated:
		user = User.query.get_or_404(user_id)
		image_file = url_for('static', filename='img/avatars/' + user.image_file)
		if current_user.id == user.id:
			return redirect('account')
		else:
			return render_template('user_page.html', user=user, image_file=image_file)
	else:
		flash("Спочатку увійдіть у свій обліковий запис", 'danger')
		return redirect(url_for('login'))


# Higher role must be required
@app.route("/user/<int:user_id>/delete", methods=['POST'])
@login_required
def delete_user(user_id):
	user = User.query.get_or_404(user_id)
	posts = Post.query.filter_by(author=user)
	if user != current_user and current_user.email == 'marzique@gmail.com':
		for post in posts:
			db.session.delete(post)
		db.session.delete(user)
		db.session.commit()
		flash('Користувача і всі його новини видалено', 'success')
		return redirect(url_for('users'))
	else:
		abort(403)


@app.route('/news/<string:username>')
def username_news(username):
	# check id injection here!
	page = request.args.get('page', 1, type=int)
	user = User.query.filter_by(username=username).first_or_404()
	# LIFO
	posts = Post.query.filter_by(author=user) \
				.order_by(Post.date_posted.desc()) \
				.paginate(page=page, per_page=VAR_POST_PER_PAGE)
	return render_template('news.html', posts=posts, title="Новини", menuitem='news', user=username)


@app.errorhandler(404)
def page_not_found(e):
	# note that we set the 404 status explicitly
	return render_template('404.html'), 404


@app.route('/account/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
	if current_user.is_authenticated:
		flash('Ви вже залогінені як ' + current_user.username, 'warning')
	else:
		form = ResetRequest()
		if form.validate_on_submit():
			user = User.query.filter_by(email=form.email.data.lower()).first()
			if user:
				pass_token = generate_password_token(user.email)
				msg = Message('Зміна паролю', sender='marzique@gmail.com', recipients=[user.email])
				reset_url = url_for('reset_password', reset_token=pass_token, _external=True)
				msg.html = render_template('emails/reset_password_email.html', full_link=reset_url)
				try:
					mail.send(msg)
					flash('На вказану адресу ' + user.email + ' були вислані інструкції по зміні пароля,\
						  якщо ви не маєте доступу до цієї адреси зверніться до адміністратора', 'success')
					return redirect(url_for('login'))
				# catch GMAIL/SMTP error here
				except SMTPException:
					flash('Щось пішло не так, спробуйте пізніше або зверніться до адміністратора!', 'danger')
			else:
				flash('Користувач з такою поштовою скринькою не зареєстрований', 'danger')

		return render_template('reset_password_request.html', form=form, title="Змінити пароль")


@app.route('/account/reset_password/<reset_token>', methods=['GET', 'POST'])
def reset_password(reset_token):
	try:
		signature = URLSafeTimedSerializer(VAR_SAFE_TIMED_KEY)
		# check if URL correct and still valid
		email = signature.loads(reset_token, salt=VAR_PASSWORD_SALT, max_age=VAR_TOKEN_MAX_AGE)
	except SignatureExpired:
		return '<h1>Старе посилання. Для підтвердження пошти зверніться до адміністратора.</h1><br> \
			   <a href="' + url_for("index") + '">Повернутись на сайт</a>'

	except BadSignature:
		return '<h1>Посилання не є дійсним. Для підтвердження пошти перейдіть по посиланню надісланому вам на пошту \
				або зверніться до адміністратора.</h1><br> \
						   <a href="' + url_for("index") + '">Повернутись на сайт</a>'

	form = ResetPassword()
	if form.validate_on_submit():
		if password_check(form.password.data):
			user = User.query.filter_by(email=email).first_or_404()
			user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
			db.session.commit()
			flash('Новий пароль встановлено!', 'success')
		else:
			flash(
				'Ваш пароль дуже слабкий, спробуйте додати Великі, малі літери, цифри, та спеціальні символи. '
				'Пароль має складатись з щонайменше ' + str(VAR_MIN_PASS_LEN) + ' символів', 'danger')

	return render_template('reset_password.html', form=form, title="Змінити пароль")


