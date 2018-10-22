import re
import os
import secrets
from PIL import Image
from rpd_site import app
from itsdangerous import URLSafeTimedSerializer
from rpd_site.constants import VAR_MAIL_SALT, VAR_SAFE_TIMED_KEY

"""
All useful functions for routes
"""


def password_check(password):
	"""
	Verify the strength of 'password'
	A password is considered strong if:
		8 characters length or more
		1 digit or more
		1 symbol or more
		1 uppercase letter or more
		1 lowercase letter or more
		returns True if all checks passed
		https://stackoverflow.com/a/32542964/10103803
	"""

	# length
	length_error = len(password) < 8
	# digits
	digit_error = re.search(r"\d", password) is None
	# uppercase
	uppercase_error = re.search(r"[A-Z]", password) is None
	# lowercase
	lowercase_error = re.search(r"[a-z]", password) is None
	# symbols
	symbol_error = re.search(r"\W", password) is None
	# overall result
	password_ok = not (length_error or digit_error or uppercase_error or lowercase_error or symbol_error)

	return password_ok


def save_picture(form_picture, size_crop, is_avatar):
	'''
	Uploads square-cropped image with randomised
    filename and returns it'signature filename + input extension
    '''
	random_hex = secrets.token_hex(8)
	# get image extension
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	if is_avatar:
		picture_path = os.path.join(app.root_path, 'static/img/avatars', picture_fn)
		output_size = size_crop
		i = Image.open(form_picture)
		# crop top square to leave aspect ratio
		f_width, _ = i.size
		i = i.crop((0, 0, f_width, f_width))
		i.thumbnail(output_size)
		i.save(picture_path)
	else:
		picture_path = os.path.join(app.root_path, 'static/img', picture_fn)
		output_size = size_crop
		i = Image.open(form_picture)
		i.thumbnail(output_size)
		i.save(picture_path)

	return picture_fn


def generate_confirmation_token(email):
	serializer = URLSafeTimedSerializer(VAR_SAFE_TIMED_KEY)
	return serializer.dumps(email, salt=VAR_MAIL_SALT+email)


def confirm_token(token, email_to_confirm, expiration=3600):
	serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
	try:
		email = serializer.loads(
			token,
			salt=VAR_MAIL_SALT+email_to_confirm,
            max_age=expiration
        )
	except SignatureExpired:
		return '<h1>Старе посилання. Для підтвердження пошти зверніться до адміністратора.</h1><br> \
        		   <a href="' + url_for("index") + '">Повернутись на сайт</a>'

	except BadSignature:
		return '<h1>Посилання не є дійсним. Для підтвердження пошти перейдіть по посиланню надісланому вам на пошту \
        			або зверніться до адміністратора.</h1><br> \
        					   <a href="' + url_for("index") + '">Повернутись на сайт</a>'
	return email