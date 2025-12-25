from flask import Blueprint, render_template, redirect, url_for, request, make_response
from flask_babel import _
from common.config import globals
from common.models import plots as pl
from web.actions import chia, plotman, worker, stats, warnings
from web.utils import get_lang, find_selected_worker
import traceback

farming_bp = Blueprint('farming', __name__)

@farming_bp.route('/farming/plots', methods=['GET', 'POST'])
def plots():
    if request.method == 'POST':
        settings = { 'replotting': plotman.save_replotting_settings(request.form) }
    else: # Get so load defaults or get saved settings
        settings = { 'replotting': plotman.load_replotting_settings() }
    if request.args.get('analyze'):  # Xhr with a plot_id
        plot_id = request.args.get('analyze')
        return plotman.analyze(plot_id[:8])
    elif request.args.get('check'):  # Xhr with a plot_id
        return chia.check(request.args.get('check'), request.args.get('force_recheck', default=False, type=lambda v: v.lower() == 'true'))
    gc = globals.load()
    farmers = chia.load_farmers()
    plots = chia.load_plots_farming()
    return render_template('farming/plots.html', farmers=farmers, plots=plots, 
        settings=settings, ksizes=pl.KSIZES, global_config=gc, lang=get_lang(request))

@farming_bp.route('/farming/data')
def data():
    try:
        [draw, recordsTotal, recordsFiltered, data] = chia.load_plots(request.args)
        return make_response({'draw': draw, 'recordsTotal': recordsTotal, 'recordsFiltered': recordsFiltered, "data": data}, 200)
    except: 
        traceback.print_exc()
    return make_response(_("Error! Please see logs."), 500)

@farming_bp.route('/farming/workers')
def workers():
    gc = globals.load()
    farmers = chia.load_farmers()
    daily_summaries = stats.load_daily_farming_summaries(farmers)
    disk_usage = stats.load_current_disk_usage('plots')
    stats.set_disk_usage_per_farmer(farmers, disk_usage)
    mem_usage = stats.load_recent_mem_usage('farming')
    return render_template('farming/workers.html', farmers=farmers, 
        daily_summaries=daily_summaries, disk_usage=disk_usage, mem_usage=mem_usage, 
        MAX_COLUMNS_ON_CHART=stats.MAX_ALLOWED_PATHS_ON_BAR_CHART,
        global_config=gc)

@farming_bp.route('/farming/warnings', methods=['GET', 'POST'])
def warnings_page(): # Renamed from 'warnings' to avoid conflict with imported warnings module
    gc = globals.load()
    if request.method == 'POST':
        if request.form.get('action') == 'clear':
            warnings.clear_plot_warnings()
    farmers = chia.load_farmers()
    plot_warnings = warnings.load_plot_warnings()
    return render_template('farming/warnings.html', farmers=farmers, 
        plot_warnings=plot_warnings, global_config=gc, lang=get_lang(request))

@farming_bp.route('/settings/farming', methods=['GET', 'POST'])
def settings():
    selected_worker_hostname = None
    blockchains = globals.enabled_blockchains()
    selected_blockchain = None
    gc = globals.load()
    if request.method == 'POST':
        selected_worker_hostname = request.form.get('worker')
        selected_blockchain = request.form.get('blockchain')
        chia.save_config(worker.get_worker(selected_worker_hostname, selected_blockchain), selected_blockchain, request.form.get("config"))
    workers_summary = worker.load_worker_summary()
    selected_worker = find_selected_worker(workers_summary.farmers_harvesters(), selected_worker_hostname, selected_blockchain)
    hot_addresses = chia.load_hot_wallet_addresses()
    cold_addresses = chia.load_cold_wallet_addresses()
    if not selected_blockchain:
        selected_blockchain = selected_worker['blockchain']
    return render_template('settings/farming.html', blockchains=blockchains, selected_blockchain=selected_blockchain,
        workers=workers_summary.farmers_harvesters, selected_worker=selected_worker['hostname'], 
        hot_addresses=hot_addresses, cold_addresses=cold_addresses, global_config=gc)
