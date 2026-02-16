from flask import Blueprint, render_template
from web import utils

controller_bp = Blueprint('controller', __name__)

@controller_bp.route('/controller')
def controller():
    return render_template('controller.html', controller_url = utils.get_controller_web())
