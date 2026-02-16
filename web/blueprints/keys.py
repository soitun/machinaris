from flask import Blueprint, render_template
from common.config import globals
from web.actions import chia, worker

keys_bp = Blueprint('keys', __name__)

@keys_bp.route('/keys')
def index():
    gc = globals.load()
    selected_blockchain = worker.default_blockchain()
    keys = chia.load_keys()
    key_paths = globals.get_key_paths()
    return render_template('keys.html', keys=keys, selected_blockchain = selected_blockchain,
        key_paths=key_paths, global_config=gc)
