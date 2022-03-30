from flask_login import current_user
from app.models import Card, Target, Appearance, Ignore, Variant
from app import db
from datetime import date
from  sqlalchemy.sql.expression import func
import re

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

def parseContent(content):
    content = content.lower()
    sentenceList = re.split(r"[.|!|\\?|\n]", content)
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
