from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.models import User
from app.forms import RegistrationForm, RepeatCard, CompleteCard
from datetime import date, timedelta
from app.helpers import *


@app.route('/')
@app.route('/index')
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

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html', title='Settings')

@app.route('/learn')
@login_required
def learn():
    return render_template('learn.html', title='Learn')

@app.route('/flashcards', methods=['GET', 'POST'])
@login_required
def flashcards():
    flashcards = getFlashcards()
    repeatForm = RepeatCard()
    completeForm = CompleteCard()
    if not flashcards:
        flash('You have reviewed all due cards!')
        return render_template('learn.html', title='Learn')
    if request.method == 'POST':
        form = request.form["submit"]
        if form == 'Complete':
            card = flashcards[0]
            if card.status == 'new' or card.status == 'repeat':
                card.status = 'learning'
            if card.lastInterval == 0 or card.lastInterval == 1:
                card.lastInterval += 1
            else:
                card.lastInterval = round(card.lastInterval * 1.5)
            card.nextReviewDate = date.today() + timedelta(days=card.lastInterval)
            if card.lastInterval > 120:
                card.status = 'expert'
            elif card.lastInterval > 60:
                card.status = 'familiar'
            db.session.commit()
            flashcards = getFlashcards()
        elif form == 'Repeat':
            card = flashcards[0]
            card.status = 'repeat'
            card.lastInterval = 0
            db.session.commit()
            flashcards = getFlashcards()
    if not flashcards:
        flash('You have reviewed all due cards!')
        return render_template('learn.html', title='Learn')
    return render_template('flashcards.html', title='Flashcards', flashcards=flashcards, flashcard=flashcards[0], repeatForm=repeatForm, completeForm=completeForm)

@app.route('/viewStats')
@login_required
def viewStats():
    stats = getStats()
    return render_template('viewStats.html', title='Stats', stats=stats)
