from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Target
from app.helpers import *

bp = Blueprint('maps', __name__)

@bp.route('/selectMap')
@login_required
def selectMap():
    targets = Target.query.filter().all()
    maps = []
    for target in targets:
        stats = getStats(target.id)
        maps.append(stats)
    return render_template('selectMap.html', title='Select Map', maps=maps)

@bp.route('/<target_id>/map')
@login_required
def map(target_id):
    thisMap = getStats(target_id)
    percent = round(100-thisMap[2])
    practiced = round(100-thisMap[3])
    return render_template('map.html', title=thisMap[0].source, percent=percent, practiced=practiced)
