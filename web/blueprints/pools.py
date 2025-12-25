from flask import Blueprint, render_template, request, flash
from flask_babel import _
from web.utils import get_lang
from common.config import globals
from common.models import pools as po
from web.actions import pools as p, worker

pools_bp = Blueprint('pools', __name__)

@pools_bp.route('/pools')
def index():
    gc = globals.load()
    selected_blockchain = worker.default_blockchain()
    return render_template('pools.html', pools= p.load_pools(), global_config=gc, selected_blockchain = selected_blockchain)

@pools_bp.route('/settings/pools', methods=['GET', 'POST'])
def settings():
    gc = globals.load()
    selected_blockchain = worker.default_blockchain()
    if request.method == 'POST':
        if request.form.get("action") == 'deleteUnconfirmed':
            p.delete_unconfirmed_transactions(request.form.get('walletid'))
        else: # Updating settings for pooling
            selected_blockchain = request.form.get('blockchain')
            selected_fullnode = worker.get_fullnode(selected_blockchain)
            launcher_ids = request.form.getlist('{0}-launcher_id'.format(selected_blockchain))
            wallet_nums = request.form.getlist('{0}-wallet_num'.format(selected_blockchain))
            choices = []
            for num in wallet_nums:
                choices.append(request.form.get('{0}-choice-{1}'.format(selected_blockchain, num)))
            pool_urls = request.form.getlist('{0}-pool_url'.format(selected_blockchain))
            current_pool_urls = request.form.getlist('{0}-current_pool_url'.format(selected_blockchain))
            fee_mojos = request.form.getlist('{0}-fee_mojos'.format(selected_blockchain))
            p.send_request(selected_fullnode, selected_blockchain, launcher_ids, choices, pool_urls, wallet_nums, current_pool_urls, fee_mojos)
    pool_configs = p.get_pool_configs()
    fullnodes_by_blockchain = worker.get_fullnodes_by_blockchain()
    poolable_blockchains = []
    for pb in po.POOLABLE_BLOCKCHAINS:
        if pb in fullnodes_by_blockchain:
            poolable_blockchains.append(pb)
    return render_template('settings/pools.html',  global_config=gc, fullnodes_by_blockchain=fullnodes_by_blockchain,
        pool_configs=pool_configs, blockchains=poolable_blockchains, selected_blockchain=selected_blockchain)
