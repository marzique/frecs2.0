import re
import os
import secrets
from PIL import Image
from rpd_site import app

"""
All useful functions for routes
"""


def password_check(password):
	"""
	Verify the strength of 'password'
	Returns a dict indicating the wrong criteria
	A password is considered strong if:
		8 characters length or more
		1 digit or more
		1 symbol or more
		1 uppercase letter or more
		1 lowercase letter or more
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
