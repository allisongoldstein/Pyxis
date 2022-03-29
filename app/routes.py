from lib2to3.pgen2.token import PERCENTEQUAL
from os import curdir, stat_result
import string
from urllib.parse import urlparse
from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from app.models import Card, User, Target, Temp, Ignore, Variant, Appearance
from app import db
from app.forms import RegistrationForm, AddCard, EditCard, AddTarget, RepeatCard, CompleteCard
from sqlalchemy import delete, cast
from datetime import datetime, date, timedelta
from  sqlalchemy.sql.expression import func, select
import re

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

@app.route('/viewCards')
@login_required
def viewCards():
    cards = Card.query.filter_by(user_id=current_user.id).order_by(Card.word)
    return render_template('viewCards.html', title='View Cards', cards=cards)

@app.route('/addCard', methods=['GET', 'POST'])
@login_required
def addCard():
    form = AddCard()
    if form.validate_on_submit():
        card = Card.query.filter_by(word=form.word.data.lower(), user_id=current_user.id).first()
        if card:
            flash('Card already in deck!')
            return redirect(url_for('viewCards'))
        list = [(form.word.data.lower(), form.translation.data)]
        addFromList(list)
        flash('You have successfully added ' + form.word.data + ' to your deck!')
        return redirect(url_for('viewCards'))
    return render_template('addCard.html', title='Add New Card', form=form)

@app.route('/ignores', methods=['GET', 'POST'])
@login_required
def ignores():
    ignores = Ignore.query.filter().order_by(Ignore.ignWord)
    return render_template('ignores.html', title='Manage Ignores', ignores=ignores)

@app.route('/<ignoreID>/deleteIgnore', methods=["POST"])
@login_required
def deleteIgnore(ignoreID):
    ignore = Ignore.query.filter_by(id=ignoreID).first()
    db.session.delete(ignore)
    db.session.commit()
    return redirect(url_for('ignores'))

@app.route('/variants', methods=['GET', 'POST'])
@login_required
def variants():
    variants = Variant.query.filter().order_by(Variant.varWord)
    return render_template('variants.html', title='Manage Variants', variants=variants)

@app.route('/<variantID>/deleteVariant', methods=["POST"])
@login_required
def deleteVariant(variantID):
    variant = Variant.query.filter_by(id=variantID).first()
    db.session.delete(variant)
    db.session.commit()
    return redirect(url_for('variants'))

@app.route('/<card_id>/editCard', methods=['GET', 'POST'])
@login_required
def editCard(card_id):
    card = Card.query.filter_by(id=card_id).first()
    form = EditCard(obj=card)
    if form.validate_on_submit():
        card.translation = form.translation.data
        db.session.commit()
        return redirect(url_for('viewCards'))
    return render_template('editCard.html', title='Edit Card', form=form)

@app.route('/<card_id>/deleteCard', methods=["POST"])
@login_required
def deleteCard(card_id):
    card = Card.query.filter_by(id=card_id).first()
    db.session.delete(card)
    db.session.commit()
    return redirect(url_for('viewCards'))

@app.route('/selectMap')
@login_required
def selectMap():
    targets = Target.query.filter().all()
    maps = []
    for target in targets:
        stats = getStats(target.id)
        maps.append(stats)
    return render_template('selectMap.html', title='Select Map', maps=maps)

@app.route('/<target_id>/map')
@login_required
def map(target_id):
    thisMap = getStats(target_id)
    percent = round(100-thisMap[2])
    practiced = round(100-thisMap[3])
    return render_template('map.html', title=thisMap[0].source, percent=percent, practiced=practiced)

@app.route('/addTarget', methods=['GET', 'POST'])
@login_required
def addTarget():
    form = AddTarget()
    if form.validate_on_submit():
        wordList = parseContent(form.content.data)
        tLength = len(wordList)
        target = Target(source=form.source.data, content=form.content.data, category=form.category.data, notes=form.notes.data, uniqueWordCount=tLength, user_id=current_user.id)
        db.session.add(target)
        db.session.commit()
        wordList = wordCheck(wordList, target.id)
        if not wordList:
            flash('Target added, no new cards.')
            return redirect(url_for('viewCards', title='View Cards'))
        wl = " ".join(wordList)
        temp = Temp(listString=wl, target_id=target.id, user_id=current_user.id)
        db.session.add(temp)
        db.session.commit()
        return redirect(url_for('filterNewWords', id=temp.id))
    return render_template('addTarget.html', title='Add Target', form=form)

def parseContent(content):
    content = content.lower()
    sentenceList = re.split(r"[.|!|\\?]", content)
    for i in range(len(sentenceList)):
        sentence = sentenceList[i]
        if sentence:
            while sentence[0] == " ":
                sentenceList[i] = sentence[1:]
                sentence = sentenceList[i]

    wordList = []
    for sentence in sentenceList:
        words = sentence.split(' ')
        wl = []
        for i in range(len(words)):
            word = words[i].lower()
            if word.isnumeric():
                word = ""
            elif not word.isalpha():
                while word and not word[0].isalpha():
                    word = word[1:]
                while word and not word[-1].isalpha():
                    word = word[:-1]
                words[i] = word.lower()
            if word:
                wl.append(word)
        wordList.extend(wl)
    return set(wordList)

def wordCheck(words, target_id):
    target = Target.query.filter_by(id=target_id).first()
    newList = []
    for word in words:
        w = Card.query.filter_by(word=word).first()
        i = Ignore.query.filter_by(ignWord=word).first()
        v = Variant.query.filter_by(varWord=word).first()
        if w or i or v:
            if w:
                newID = w.id
            elif i:
                newID = i.id
            elif v:
                newID = v.id
            apr = Appearance(word_id=newID, target_id=target.id, user_id=current_user.id)
            db.session.add(apr)
            db.session.commit()
        else:
            newList.append(word)
    return newList

@app.route('/<id>/filterNewWords.html', methods=['GET', 'POST'])
@login_required
def filterNewWords(id):
    wl = Temp.query.filter_by(id=id).first()
    words = wl.listString.split(" ")
    if request.method == 'POST':
        adds = []
        igns = []
        vars = []
        for word in words:
            req = request.form[word]
            adtl = word + '-adtl'
            if req == 'add':
                translation = request.form[adtl]
                adds.append((word, translation))
            elif req == 'ignore':
                igns.append(word)
            elif req == 'variant':
                t = adtl + '-translation'
                standardForm = request.form[adtl]
                translation = request.form[t]
                vars.append((word, standardForm, translation))
        addFromList(adds, wl)
        ignoreFromList(igns)
        variantsFromList(vars, wl)
        flash('Target words sorted.')
        return redirect(url_for('viewCards'))
    return render_template('filterNewWords.html', title='Filter New Words', words=words)

def addFromList(words, wl_id=None, target=None):
    if wl_id:
        target = Target.query.filter_by(id=wl_id.target_id).first()
    for word in words:
        dueDate = date.today()
        card = Card(word=word[0], translation=word[1], status='new', nextReviewDate=dueDate, lastInterval=0, user_id=current_user.id)
        db.session.add(card)
        db.session.commit()
        if target:
            card = Card.query.filter_by(word=word[0]).first()
            apr = Appearance(word_id=card.id, target_id=target.id, user_id=current_user.id)
            db.session.add(apr)
            db.session.commit()
    return

def ignoreFromList(words):
    for word in words:
        ignore = Ignore(ignWord=word, user_id=current_user.id)
        db.session.add(ignore)
        db.session.commit()
    return

def variantsFromList(words, wl_id=None, target=None):
    if wl_id:
        target = Target.query.filter_by(id=wl_id.target_id).first()
    for word in words:
        standard = word[1]
        translation = word[2]
        card = Card.query.filter_by(user_id=current_user.id, word=standard).first()
        if not card:
            add = [[standard, translation]]
            addFromList(add)
            card = Card.query.filter_by(word=standard, user_id=current_user.id).first()
        variant = Variant(varWord=word[0], standard_id=card.id, user_id=current_user.id)
        db.session.add(variant)
        db.session.commit()
        if target:
            card = Card.query.filter_by(word=standard, user_id=current_user.id).first()
            apr = Appearance(word_id=card.id, target_id=target.id, user_id=current_user.id)
            db.session.add(apr)
            db.session.commit()
    return

@app.route('/viewTargets')
@login_required
def viewTargets():
    targets = Target.query.filter_by(user_id=current_user.id)
    return render_template('viewTargets.html', title='View Targets', targets=targets)

@app.route('/<target_id>/deleteTarget', methods=["POST"])
@login_required
def deleteTarget(target_id):
    target = Target.query.filter_by(id=target_id).first()
    db.session.delete(target)
    db.session.commit()
    return redirect(url_for('viewTargets'))

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

def getFlashcards():
    curDate = date.today()
    flashcards = db.session.query(Card).filter(Card.nextReviewDate<=curDate, Card.status!='repeat', Card.user_id==current_user.id).all()
    if not flashcards:
        flashcards = getReviewCards()
    return flashcards

def getReviewCards():
    reviewCards = db.session.query(Card).filter(Card.status=='repeat', Card.user_id==current_user.id).order_by(func.random()).all()
    # reviewCards = db.session.query(Card).filter(Card.lastInterval>2, Card.user_id==current_user.id).all()
    return reviewCards

@app.route('/viewStats')
@login_required
def viewStats():
    stats = getStats()
    return render_template('viewStats.html', title='Stats', stats=stats)

def getStats(target=None):
    stats = []
    if target:
        targs = Target.query.filter(Target.id==target).all()
    else:
        targs = Target.query.filter_by(user_id=current_user.id).all()
    for targ in targs:
        cardStats = []
        x = Appearance.query.filter(Appearance.target_id==targ.id).all()
        newCount, learningCount, familiarCount, expertCount = 0, 0, 0, 0
        for each in x:
            card = Card.query.filter(Card.id==each.word_id).first()
            if card:
                if card.status == 'new':
                    newCount += 1
                elif card.status == 'learning' or card.status == 'repeat':
                    learningCount += 1
                elif card.status == 'familiar':
                    familiarCount += 1
                elif card.status == 'expert':
                    expertCount += 1
        cardStats = [newCount, learningCount, familiarCount, expertCount]
        percent = round(((newCount + learningCount)/(targ.uniqueWordCount) * 100))
        unseen = round(((newCount)/(targ.uniqueWordCount) * 100))
        stats.append((targ, cardStats, percent, unseen))
    if target:
        return stats[0]
    return stats
