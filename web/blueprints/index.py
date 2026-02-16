from flask import Blueprint, render_template, redirect, url_for, request, flash, send_from_directory, current_app
from flask_babel import _
from common.config import globals
from common.utils import fiat
from web import utils
from web.actions import chia, plotman, worker, stats, warnings, pools as p
from web.utils import get_lang
import os

index_bp = Blueprint('index', __name__)

@index_bp.route('/index')
def index():
    gc = globals.load()
    if not globals.is_setup():
        return redirect(url_for('setup.setup'))
    if not utils.is_controller():
        return redirect(url_for('controller.controller'))
    workers = worker.load_worker_summary()
    farm_summary = chia.load_farm_summary()
    plotting = plotman.load_plotting_summary_by_blockchains(farm_summary.farms.keys())
    if request.args.get('selected_blockchain'):
        # Check if user has pinned the view to a particular blockchain view on refresh, no rotate
        selected_blockchain = request.args.get('selected_blockchain')
        carousel_ride_enabled = False  # Disable automatic carousel rotation on load
    else: # Default is to rotate every 10 seconds
        selected_blockchain = farm_summary.selected_blockchain()
        carousel_ride_enabled = True # Enable automatic carousel rotation on load
    chia.challenges_chart_data(farm_summary)
    p.partials_chart_data(farm_summary)
    stats.load_daily_diff(farm_summary)
    stats.wallet_chart_data(farm_summary)
    warnings.check_warnings(request.args)
    return render_template('index.html', reload_seconds=120, farms=farm_summary.farms, \
        plotting=plotting, workers=workers, global_config=gc, \
        carousel_ride_enabled=carousel_ride_enabled, selected_blockchain=selected_blockchain)

@index_bp.route('/chart')
def chart():
    gc = globals.load()
    chart_type = request.args.get('type')
    blockchain = request.args.get('blockchain')
    if chart_type == 'wallet_balances':
        chart_data = stats.load_wallet_balances(blockchain)
        return render_template('charts/balances.html', reload_seconds=120, global_config=gc, chart_data=chart_data, lang=get_lang(request)) 
    elif chart_type == 'farmed_blocks':
        chart_data = stats.load_farmed_coins(blockchain)
        farmed_blocks = stats.load_farmed_blocks(blockchain)
        return render_template('charts/farmed.html', reload_seconds=120, global_config=gc, chart_data=chart_data, farmed_blocks=farmed_blocks, lang=get_lang(request))
    elif chart_type == 'netspace_size':
        chart_data = stats.load_netspace_size(blockchain)
        return render_template('charts/netspace.html', reload_seconds=120, global_config=gc, chart_data=chart_data, lang=get_lang(request))
    elif chart_type == 'plot_count':
        chart_data = stats.load_plot_count(blockchain)
        return render_template('charts/plot_count.html', reload_seconds=120, global_config=gc, chart_data=chart_data, lang=get_lang(request)) 
    elif chart_type == 'plots_size':
        chart_data = stats.load_plots_size(blockchain)
        return render_template('charts/plots_size.html', reload_seconds=120, global_config=gc, chart_data=chart_data, lang=get_lang(request)) 
    elif chart_type == 'effort':
        chart_data = stats.load_effort(blockchain)
        return render_template('charts/effort.html', reload_seconds=120, global_config=gc, chart_data=chart_data, lang=get_lang(request)) 
    elif chart_type == 'timetowin':
        chart_data = stats.load_time_to_win(blockchain)
        return render_template('charts/timetowin.html', reload_seconds=120, global_config=gc, chart_data=chart_data, lang=get_lang(request)) 
    elif chart_type == 'container_memory':
        chart_data = stats.load_container_memory(request.args.get('hostname'), blockchain)
        return render_template('charts/container_memory.html', reload_seconds=120, global_config=gc, chart_data=chart_data, lang=get_lang(request)) 

@index_bp.route('/summary', methods=['GET', 'POST'])
def summary():
    gc = globals.load()
    if request.method == 'POST':
        fiat.save_local_currency(request.form.get('local_currency'))
        flash(_("Saved local currency setting."), 'success')
    summaries = chia.load_summaries()
    fullnodes = worker.get_fullnodes_by_blockchain()
    return render_template('summary.html', reload_seconds=120, summaries=summaries, global_config=gc,
        exchange_rates=fiat.load_exchange_rates_cache(), local_currency=fiat.get_local_currency(), 
        local_cur_sym=fiat.get_local_currency_symbol(), fullnodes=fullnodes, lang=get_lang(request))

@index_bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(current_app.root_path, 'static'),
            'favicon.ico', mimetype='image/vnd.microsoft.icon')
