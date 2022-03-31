from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app.models import Target, Temp
from app import db
from app.forms import AddTarget
from app.helpers import *

bp = Blueprint('targets', __name__)

@bp.route('/addTarget', methods=['GET', 'POST'])
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
            return redirect(url_for('cards.viewCards', title='View Cards'))
        wl = " ".join(wordList)
        temp = Temp(listString=wl, target_id=target.id, user_id=current_user.id)
        db.session.add(temp)
        db.session.commit()
        return redirect(url_for('targets.filterNewWords', id=temp.id))
    return render_template('targets/addTarget.html', title='Add Target', form=form)

@bp.route('/<id>/filterNewWords.html', methods=['GET', 'POST'])
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
        return redirect(url_for('cards.viewCards'))
    return render_template('targets/filterNewWords.html', title='Filter New Words', words=words)

@bp.route('/viewTargets')
@login_required
def viewTargets():
    targets = Target.query.filter_by(user_id=current_user.id)
    return render_template('targets/viewTargets.html', title='View Targets', targets=targets)

@bp.route('/<target_id>/deleteTarget', methods=["POST"])
@login_required
def deleteTarget(target_id):
    target = Target.query.filter_by(id=target_id).first()
    db.session.delete(target)
    db.session.commit()
    return redirect(url_for('targets.viewTargets'))
