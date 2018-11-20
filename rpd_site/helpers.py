#!/usr/bin/env python
'''Helping functions'''
__author__ = 'Denys Tarnavskyi'
__copyright__ = 'Copyright 2018, RPD site project'
__license__ = 'MIT'
__version__ = '1.0'
__email__ = 'marzique@gmail.com'
__status__ = 'Development'

import re
import os
import secrets
from PIL import Image
from itsdangerous import URLSafeTimedSerializer
from rpd_site import app, db
from .constants import VAR_MAIL_SALT, VAR_SAFE_TIMED_KEY, VAR_PASSWORD_SALT, VAR_MIN_PASS_LEN
from .models import Role, User, Post


def create_role(role_name):
    '''
    adds new role to database
    '''
    role_search = Role.query.filter_by(name=role_name).first()
    if not role_search:
        role = Role(name=role_name)
        db.session.add(role)
        db.session.commit()
        return True
        print('New role ' + role_name + ' added!')
    else:
        return False


def delete_role(role_name):
    '''
    deletes new role from database
    '''
    role = Role.query.filter_by(name=role_name).first()
    if role:
        db.session.delete(role)
        db.session.commit()
        print('Role ' + role_name + ' deleted!')
    else:
        print('Role ' + role_name + ' doesn\'t exist!')


def get_all_roles():
    '''
    get's all role names from db table
    '''
    names = []
    roles = Role.query.all()
    for role in roles:
        names.append(role.name)
    return names

def get_number_of_users():
    return len(User.query.all())

def get_number_of_posts():
    return len(Post.query.all())


# All useful functions and objects for routes

def month_translation(eng_month):
    '''
    Translates month name to Ukranian
    '''
    month_translations = {'January': 'Cічня', 'February': 'Лотого', 'March': 'Березня',
                          'April': 'Квітня', 'May': 'Травня', 'June': 'Червня', 'July': 'Липня',
                          'August': 'Серпня', 'September': 'Вересня', 'October': 'Жовтня',
                          'November': 'Листопада', 'December': 'Грудня'}
    ukranian_month = month_translations[eng_month]
    return ukranian_month


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
    length_error = len(password) < VAR_MIN_PASS_LEN                                         # length
    digit_error = re.search(r"\d", password) is None                                        # digits
    uppercase_error = re.search(r"[A-Z]", password) is None                                 # uppercase
    lowercase_error = re.search(r"[a-z]", password) is None                                 # lowercase
    symbol_error = re.search(r"\W", password) is None                                       # symbols
    password_ok = not (
        length_error or digit_error or uppercase_error or lowercase_error or symbol_error)  # overall result

    return password_ok


def save_picture(form_picture, size_crop, is_avatar):
    '''
    Uploads cropped image with randomised
    filename and returns it's filename + input extension
    '''
    random_hex = secrets.token_hex(8)
    # get image extension
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    if is_avatar:
        picture_path = os.path.join(
            app.root_path, 'static/img/avatars', picture_fn)
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
    '''
    Creates unique token for each email passed
    :param email: email to create token for, used as part of the salt to make each token different.
    :return: token
    '''
    serializer = URLSafeTimedSerializer(VAR_SAFE_TIMED_KEY)
    return serializer.dumps(email, salt=VAR_MAIL_SALT + email)


def generate_password_token(email):
    serializer = URLSafeTimedSerializer(VAR_SAFE_TIMED_KEY)
    return serializer.dumps(email, salt=VAR_PASSWORD_SALT)


def role_label(role_name):
    '''generate HTML button snippet for role'''
    label_classes = {'unconfirmed': 'btn-default',
                      'confirmed': 'btn-primary',
                     'admin': 'btn-success',
                     'student': 'btn-info',
                     'teacher': 'btn-warning',
                     'moderator': 'btn-danger'
                     }

    return '<button type="button" style="padding: 2px;" data-whatever="' + role_name + '"\
    data-toggle="modal" data-target="#deleteModal" class="btn btn-sm '\
     + label_classes[role_name] + '">' + role_name + '</button>'

# TODO: rename span to button (figure out how to refactor variable across all files like in PyCharm)
def role_spans(user):
    '''Generate list of role spans(buttons!) for specific user'''
    spans = []
    roles = user.get_roles()
    for role in roles:
        span = role_label(role)
        spans.append(span)
    return spans
    