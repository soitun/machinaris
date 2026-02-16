from flask import Blueprint, render_template, request, url_for
from web.utils import get_lang
from common.config import globals
from web.actions import worker, stats, plotman

workers_bp = Blueprint('workers', __name__)

@workers_bp.route('/workers', methods=['GET', 'POST'])
def index():
    gc = globals.load()
    if request.method == 'POST':
        if request.form.get('action') == "prune":
            worker.prune_workers_status(request.form.getlist('worker'))
    wkrs = worker.load_worker_summary()
    chart_data = stats.load_host_memory_usage()
    return render_template('workers.html', reload_seconds=120, 
        workers=wkrs, global_config=gc, chart_data=chart_data, lang=get_lang(request))

@workers_bp.route('/worker', methods=['GET'])
def worker_route():
    gc = globals.load()
    hostname=request.args.get('hostname')
    blockchain=request.args.get('blockchain')
    wkr = worker.get_worker(hostname, blockchain)
    plotting = plotman.load_plotting_summary(hostname=hostname)
    plots_disk_usage = stats.load_current_disk_usage('plots',hostname=hostname)
    plotting_disk_usage = stats.load_current_disk_usage('plotting',hostname=hostname)
    mem_usage = stats.load_recent_mem_usage('all', only_hostname=hostname, only_blockchain=blockchain)
    warnings = worker.generate_warnings(wkr)
    return render_template('worker.html', worker=wkr, 
        plotting=plotting, mem_usage=mem_usage, plots_disk_usage=plots_disk_usage, 
        plotting_disk_usage=plotting_disk_usage, warnings=warnings, global_config=gc,
        MAX_COLUMNS_ON_CHART=stats.MAX_ALLOWED_PATHS_ON_BAR_CHART,
        lang=get_lang(request))

@workers_bp.route('/worker_launch')
def launch():
    [farmer_pk, pool_pk, pool_contract_address] = plotman.load_plotting_keys('chia')
    return render_template('worker_launch.html', farmer_pk=farmer_pk, 
        pool_pk=pool_pk, pool_contract_address=pool_contract_address)
