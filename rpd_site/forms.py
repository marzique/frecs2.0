from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from rpd_site.models import User


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
            raise ValidationError('Користувач з таким іменем вже зареєстрований')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Користувач з такою поштовою скринькою вже зареєстрований')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запам&#39ятати')
    submit = SubmitField('Увійти')