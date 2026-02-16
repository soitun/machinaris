from flask import Blueprint, render_template, request, flash
from flask_babel import _
from web.utils import get_lang
from common.config import globals
from common.utils import fiat
from web.actions import chia, worker

blockchains_bp = Blueprint('blockchains', __name__)

@blockchains_bp.route('/blockchains', methods=['GET','POST'])
def index():
    gc = globals.load()
    if request.method == 'POST':
        if request.form.get('local_currency'):
            fiat.save_local_currency(request.form.get('local_currency'))
            flash(_("Saved local currency setting."), 'success')
        elif request.form.get('blockchain'):
            chia.restart_farmer(request.form.get('hostname'), request.form.get('blockchain'))
            flash(_("Restarting blockchain.  Please allow at least 15 minutes..."), 'success')
    selected_blockchain = worker.default_blockchain()
    blockchains = chia.load_blockchains()
    fullnodes = worker.get_fullnodes_by_blockchain()
    return render_template('blockchains.html', reload_seconds=120, selected_blockchain = selected_blockchain, 
        blockchains=blockchains, exchange_rates=fiat.load_exchange_rates_cache(), local_currency=fiat.get_local_currency(), 
        local_cur_sym=fiat.get_local_currency_symbol(), fullnodes=fullnodes, global_config=gc, lang=get_lang(request))
