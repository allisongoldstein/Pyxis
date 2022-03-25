from urllib.parse import urlparse
from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from app.models import Card, User, Target
from app import db
from app.forms import RegistrationForm, AddCard, EditCard, AddTarget
from sqlalchemy import delete
import re

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

@app.route('/viewCards')
@login_required
def viewCards():
    cards = Card.query.all()
    return render_template('viewCards.html', title='View Cards', cards=cards)

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

@app.route('/<cardID>/editCard', methods=['GET', 'POST'])
@login_required
def editCard(cardID):
    card = Card.query.filter_by(id=cardID).first()
    form = EditCard(obj=card)
    if form.validate_on_submit():
        card.translation = form.translation.data
        db.session.commit()
        cards = Card.query.all()
        return redirect(url_for('viewCards'))
    return render_template('editCard.html', title='Edit Card', form=form)

@app.route('/<cardID>/deleteCard', methods=["POST"])
@login_required
def deleteCard(cardID):
    print(cardID)
    card = Card.query.filter_by(id=cardID).first()
    db.session.delete(card)
    db.session.commit()
    return redirect(url_for('viewCards'))

@app.route('/map')
@login_required
def map():
    vis = '100%'
    return render_template('map.html', title='Map', vis=vis)

@app.route('/addTarget', methods=['GET', 'POST'])
@login_required
def addTarget():
    form = AddTarget()
    if form.validate_on_submit():
        target = Target(source=form.source.data, content=form.content.data, category=form.category.data, notes=form.notes.data)
        db.session.add(target)
        db.session.commit()
        flash('You have successfully added ' + form.source.data + ' as a target.')
        wordList = parseContent(form.content.data)
        wordCheck(wordList)
        print(wordList)
        return redirect(url_for('viewCards'))
    return render_template('addTarget.html', title='Add Target', form=form)

def parseContent(content):
    content = content.lower()
    sentenceList = re.split(r"[.|!|\\?]", content)
    for i in range(len(sentenceList)):
        sentence = sentenceList[i]
        if sentence == "":
            del sentenceList[i]
        else:
            while sentence[0] == " ":
                sentenceList[i] = sentence[1:]
                sentence = sentenceList[i]

    wordList = []
    for sentence in sentenceList:
        words = sentence.split(' ')
        for i in range(len(words)):
            word = words[i].lower()
            if word.isnumeric():
                print(word)
            elif not word.isalpha():
                print(word)
                while word and not word[0].isalpha():
                    word = word[1:]
                while word and not word[-1].isalpha():
                    word = word[:-1]
                print(word)
                words[i] = word.lower()
        wordList.extend(words)
    return wordList

def wordCheck(words):
    for word in words:
        w = Card.query.filter_by(word=word).first()
        if w is None:
            card = Card(word=word)
            db.session.add(card)
            db.session.commit()

