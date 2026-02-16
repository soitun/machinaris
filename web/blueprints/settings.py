from flask import Blueprint, render_template, request, make_response, abort, current_app
from markupsafe import escape
from flask_babel import _, lazy_gettext as _l
from common.config import globals
from web.actions import forktools, worker, chiadog, chia, plotman
from web.utils import find_selected_worker
import requests

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings/tools', methods=['GET', 'POST'])
def tools():
    selected_worker_hostname = None
    blockchains = globals.enabled_blockchains()
    selected_blockchain = None
    gc = globals.load()
    if request.method == 'POST':
        selected_worker_hostname = request.form.get('worker')
        selected_blockchain = request.form.get('blockchain')
        forktools.save_config(worker.get_worker(selected_worker_hostname, selected_blockchain), selected_blockchain, request.form.get("config"))
    farmers = chiadog.load_farmers()
    selected_worker = find_selected_worker(farmers, selected_worker_hostname, selected_blockchain)
    if not selected_blockchain:
        selected_blockchain = selected_worker['blockchain']
    return render_template('settings/tools.html', blockchains=blockchains, selected_blockchain=selected_blockchain,
        workers=farmers, selected_worker=selected_worker['hostname'], global_config=gc)

@settings_bp.route('/settings/config', defaults={'path': ''})
@settings_bp.route('/settings/config/<path:path>')
def config(path):
    config_type = request.args.get('type')
    w = worker.get_worker(request.args.get('worker'), request.args.get('blockchain'))
    if not w:
        current_app.logger.info(_l("No worker at %(worker)s for blockchain %(blockchain)s. Please select another blockchain.",
            worker=request.args.get('worker'), blockchain=request.args.get('blockchain')))
        abort(404)
    response = None
    try:
        if config_type == "alerts":
            response = make_response(chiadog.load_config(w, request.args.get('blockchain')), 200)
        elif config_type == "farming":
            response = make_response(chia.load_config(w, request.args.get('blockchain')), 200)
        elif config_type == "plotting":
            [replaced, config] = plotman.load_config(w, request.args.get('blockchain'))
            response = make_response(config, 200)
            response.headers.set('ConfigReplacementsOccurred', replaced)
        elif config_type == "plotting_dirs":
            response = make_response(plotman.load_dirs(w, request.args.get('blockchain')), 200)
        elif config_type == "plotting_schedule":
            response = make_response(plotman.load_schedule(w, request.args.get('blockchain')), 200)
        elif config_type == "tools":
            response = make_response(forktools.load_config(w, request.args.get('blockchain')), 200)
        else:
            abort(400, "Unsupported config type: {0}".format(config_type))
    except requests.exceptions.ConnectionError as ex:
        response = make_response(_("No responding fullnode found for %(blockchain)s. Please check your workers.", blockchain=escape(request.args.get('blockchain'))))
    
    if response:
        response.mimetype = "application/x-yaml"
    return response
