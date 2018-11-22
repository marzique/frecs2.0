#!/usr/bin/env python
'''All form models'''
__author__ = 'Denys Tarnavskyi'
__copyright__ = 'Copyright 2018, RPD site project'
__license__ = 'MIT'
__version__ = '1.0'
__email__ = 'marzique@gmail.com'
__status__ = 'Development'

from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from .models import User
from .helpers import get_all_roles, get_role_tuples


class RegistrationForm(FlaskForm):
    username = StringField('Ім&#39я користувача',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Пароль ще раз',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Підтвердити')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'Користувач з таким іменем вже зареєстрований')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'Користувач з такою поштовою скринькою вже зареєстрований')


# Email+password authentication model
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запам&#39ятати')
    submit = SubmitField('Увійти')
    recaptcha = RecaptchaField()


class UpdateAccountForm(FlaskForm):
    username = StringField('Ім&#39я користувача',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])

    submit = SubmitField('Змінити')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    'Користувач з таким іменем вже зареєстрований')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    'Користувач з такою поштовою скринькою вже зареєстрований')


class UpdatePicture(FlaskForm):
    picture = FileField('Змінити зображення користувача', validators=[
                        FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Змінити')


class PostForm(FlaskForm):
    title = StringField('Назва', validators=[
                        DataRequired(), Length(min=5, max=100)])
    content = TextAreaField('Зміст', validators=[DataRequired()])
    picture = FileField('Зображення', validators=[
                        FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Додати новину')


class ResetRequest(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Надіслати')


class ResetPassword(FlaskForm):
    password = PasswordField('Новый пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Пароль ще раз',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Змінити пароль')


class NewRole(FlaskForm):
    role = StringField('Назва Ролі',
                       validators=[DataRequired(), Length(min=4, max=15)])
    submit = SubmitField('Додати')


class AddRole(FlaskForm):
    role = SelectField(label='Роль', choices=get_role_tuples())
    submit = SubmitField('Надати роль')

    
class UploadFile(FlaskForm):
    '''
    Uploads files for students
    '''
    name = StringField('Назва', validators=[
                        DataRequired(), Length(min=5, max=100)])
    course = StringField('Предмет', validators=[
                        DataRequired(), Length(min=5, max=100)])
    # TODO: what extensions we will allow here?
    file = FileField('Файл', validators=[
                        FileAllowed(['jpg', 'jpeg', 'png'])])

    submit = SubmitField('Додати роль')

