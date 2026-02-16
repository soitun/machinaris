from flask import Blueprint, render_template, redirect, url_for, request
from flask_babel import _
from common.config import globals
from web.actions import worker, chiadog
from web.utils import get_lang, find_selected_worker

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/alerts', methods=['GET', 'POST'])
def alerts():
    gc = globals.load()
    if request.method == 'POST':
        if request.form.get('action') == 'start':
            w = worker.get_worker(request.form.get('hostname'))
            chiadog.start_chiadog(w)
        elif request.form.get('action') == 'stop':
            w = worker.get_worker(request.form.get('hostname'))
            chiadog.stop_chiadog(w)
        elif request.form.get('action') == 'remove':
            chiadog.remove_alerts(request.form.getlist('unique_id'))
        elif request.form.get('action') == 'purge':
            chiadog.remove_all_alerts()
        else:
            # app.logger.info(_("Unknown alerts form") + ": {0}".format(request.form))
            pass
        return redirect(url_for('alerts.alerts')) # Force a redirect to allow time to update status
    farmers = chiadog.load_farmers()
    notifications = chiadog.get_notifications()
    return render_template('alerts.html', reload_seconds=120, farmers=farmers,
        notifications=notifications, global_config=gc, lang=get_lang(request))

@alerts_bp.route('/settings/alerts', methods=['GET', 'POST'])
def settings():
    selected_worker_hostname = None
    blockchains = globals.enabled_blockchains()
    selected_blockchain = None
    gc = globals.load()
    if request.method == 'POST':
        selected_worker_hostname = request.form.get('worker')
        selected_blockchain = request.form.get('blockchain')
        selected_worker = worker.get_worker(selected_worker_hostname, selected_blockchain)
        if request.form.get('action') == 'test':
            chiadog.send_test_alert(selected_worker)
            return redirect(url_for('alerts.alerts')) # Redirct to page showing the test alert
        else: # Save config
            chiadog.save_config(selected_worker, selected_blockchain, request.form.get("config"))
    farmers = chiadog.load_farmers()
    selected_worker = find_selected_worker(farmers, selected_worker_hostname, selected_blockchain)
    if not selected_blockchain:
        selected_blockchain = selected_worker['blockchain']
    return render_template('settings/alerts.html', blockchains=blockchains, selected_blockchain=selected_blockchain,
        workers=farmers, selected_worker=selected_worker['hostname'], global_config=gc)
