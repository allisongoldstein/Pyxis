from urllib.parse import urlparse
from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from app.models import Card, User
from app import db
from app.forms import RegistrationForm, AddCard

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
        # flash('Login requested for user {}, remember_me={}'.format(
        #     form.username.data, form.remember_me.data))
        # return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered.')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/addCard', methods=['GET', 'POST'])
@login_required
def addCard():
    form = AddCard()
    if form.validate_on_submit():
        card = Card(word=form.word.data, translation=form.translation.data)
        db.session.add(card)
        db.session.commit()
        flash('You have successfully added ' + form.word.data + ' to your deck!')
        return redirect(url_for('index'))
    return render_template('addCard.html', title='Add New Card', form=form)

@app.route('/map')
@login_required
def map():
    return render_template('map.html')
