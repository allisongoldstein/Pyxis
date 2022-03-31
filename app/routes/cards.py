from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.models import Card, Ignore, Variant
from app import db
from app.forms import AddCard, EditCard
from app.helpers import *

bp = Blueprint('cards', __name__)

@bp.route('/viewCards')
@login_required
def viewCards():
    cards = Card.query.filter_by(user_id=current_user.id).order_by(Card.word)
    return render_template('cards/viewCards.html', title='View Cards', cards=cards)

@bp.route('/addCard', methods=['GET', 'POST'])
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
        return redirect(url_for('cards.viewCards'))
    return render_template('cards/addCard.html', title='Add New Card', form=form)

@bp.route('/<card_id>/editCard', methods=['GET', 'POST'])
@login_required
def editCard(card_id):
    card = Card.query.filter_by(id=card_id).first()
    form = EditCard(obj=card)
    if form.validate_on_submit():
        card.translation = form.translation.data
        db.session.commit()
        return redirect(url_for('cards.viewCards'))
    return render_template('cards/editCard.html', title='Edit Card', form=form)

@bp.route('/<card_id>/deleteCard', methods=["POST"])
@login_required
def deleteCard(card_id):
    card = Card.query.filter_by(id=card_id).first()
    db.session.delete(card)
    db.session.commit()
    return redirect(url_for('cards.viewCards'))

@bp.route('/ignores', methods=['GET', 'POST'])
@login_required
def ignores():
    ignores = Ignore.query.filter().order_by(Ignore.ignWord)
    return render_template('cards/ignores.html', title='Manage Ignores', ignores=ignores)

@bp.route('/<ignoreID>/deleteIgnore', methods=["POST"])
@login_required
def deleteIgnore(ignoreID):
    ignore = Ignore.query.filter_by(id=ignoreID).first()
    db.session.delete(ignore)
    db.session.commit()
    return redirect(url_for('cards.ignores'))

@bp.route('/variants', methods=['GET', 'POST'])
@login_required
def variants():
    variants = Variant.query.filter().order_by(Variant.varWord)
    return render_template('cards/variants.html', title='Manage Variants', variants=variants)

@bp.route('/<variantID>/deleteVariant', methods=["POST"])
@login_required
def deleteVariant(variantID):
    variant = Variant.query.filter_by(id=variantID).first()
    db.session.delete(variant)
    db.session.commit()
    return redirect(url_for('cards.variants'))
