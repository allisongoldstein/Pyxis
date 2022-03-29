from wsgiref import validate
from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User
from app.models import Card

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class AddCard(FlaskForm):
    word = StringField('Word', validators=[DataRequired()])
    translation = StringField('Translation')
    submit = SubmitField('Add')

class EditCard(FlaskForm):
    word = StringField('Word', validators=[DataRequired()])
    translation = StringField('Translation')
    submit = SubmitField('Save')

class AddTarget(FlaskForm):
    source = StringField('Source', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    category = StringField('Category')
    notes = TextAreaField('Notes')
    submit = SubmitField('Add')

class RepeatCard(FlaskForm):
    formValue = 'repeat'
    submit = SubmitField('Repeat')

class CompleteCard(FlaskForm):
    formValue = 'complete'
    submit = SubmitField('Complete')