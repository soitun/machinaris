from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_babel import _
from common.config import globals
from common.utils import fiat
from web.actions import chia, pools as p, stats, worker
from web.utils import get_lang
import json

wallet_bp = Blueprint('wallet', __name__)

@wallet_bp.route('/wallet', methods=['GET', 'POST'])    
def index():
    gc = globals.load()
    selected_blockchain = worker.default_blockchain()
    if request.method == 'POST':
        if request.form.get('local_currency'):
            current_app.logger.info("Saving local currency setting of: {0}".format(request.form.get('local_currency')))
            fiat.save_local_currency(request.form.get('local_currency'))
            current_app.logger.info("Saving local currency setting of: {0}".format(request.form.get('local_currency')))
            chia.save_current_wallet_sync_frequency(request.form.get('sync_wallet_frequency'))
            flash(_("Saved local currency and wallet sync settings."), 'success')
        elif request.form.get('cold_wallet_address'):
            current_app.logger.info("Saving {0} cold wallet address of: {1}".format(request.form.get('blockchain'), request.form.get('cold_wallet_address')))
            selected_blockchain = request.form.get('blockchain')
            chia.save_cold_wallet_addresses(request.form.get('blockchain'), request.form.get('cold_wallet_address'))
        elif request.form.get('blockchain'):
            action = request.form.get('action')
            if action == "start":
                chia.start_or_pause_wallet(request.form.get('hostname'), request.form.get('blockchain'), action)
                flash(_("Starting wallet sync.  Please allow at least 15 minutes..."), 'success')
            elif action == "pause":
                chia.start_or_pause_wallet(request.form.get('hostname'), request.form.get('blockchain'), action)
                flash(_("Pausing wallet sync.  Please allow a few minutes..."), 'success')
        elif request.form.get('action') == 'recover':
            p.request_unclaimed_plotnft_reward_recovery()
        else:
            current_app.logger.error("Unknown wallet page form submitted.  No action taken.")
    if request.args.get('rewards'):
        return json.dumps(p.get_unclaimed_plotnft_rewards()), 200
    wallets = chia.load_wallets()
    sync_wallet_frequencies = chia.load_wallet_sync_frequencies()
    sync_wallet_frequency = chia.load_current_wallet_sync_frequency()
    chart_data = stats.load_total_balances(fiat.get_local_currency_symbol().lower())
    return render_template('wallet.html', wallets=wallets, global_config=gc, selected_blockchain = selected_blockchain, 
        reload_seconds=120, exchange_rates=fiat.load_exchange_rates_cache(), local_currency=fiat.get_local_currency(), 
        chart_data=chart_data, local_cur_sym=fiat.get_local_currency_symbol(), sync_wallet_frequencies=sync_wallet_frequencies, 
        sync_wallet_frequency = str(sync_wallet_frequency), lang=get_lang(request))
