from flask import Blueprint, render_template, request, abort
from flask_babel import _
from web.actions import worker, log_handler
from web.utils import get_lang

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/logs')
def index():
    return render_template('logs.html') 

@logs_bp.route('/logfile')
def file():
    w = worker.get_worker(request.args.get('hostname'), request.args.get('blockchain').lower())
    log_type = request.args.get("log")
    if log_type in [ 'alerts', 'farming', 'plotting', 'archiving', 'apisrv', 'webui', 'pooling', 'rewards']:
        log_id = request.args.get("log_id")
        blockchain = request.args.get("blockchain")
        return log_handler.get_log_lines(get_lang(request), w, log_type, log_id, blockchain)
    else:
        abort(500, _("Unsupported log type") + ": {0}".format(log_type))
