from flask import Blueprint, render_template, flash, redirect, url_for, request
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
