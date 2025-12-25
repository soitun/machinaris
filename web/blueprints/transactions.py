from flask import Blueprint, render_template, request
from web.utils import get_lang
from common.config import globals
from web.actions import chia, worker

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/transactions')
def index():
    gc = globals.load()
    blockchain=request.args.get('blockchain')
    selected_wallet_id=request.args.get('selected_wallet_id')
    w = worker.get_fullnode(blockchain=blockchain)
    trans = chia.get_transactions(get_lang(request), w, blockchain, selected_wallet_id)
    wallets = chia.load_wallet_ids(blockchain)
    return render_template('transactions.html', transactions=trans, blockchain=blockchain, wallets=wallets,
        selected_wallet_id=selected_wallet_id, reload_seconds=120, global_config=gc, lang=get_lang(request)) 
