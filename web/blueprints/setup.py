from flask import Blueprint, render_template, redirect, url_for, request, current_app
from flask_babel import _
from common.config import globals
from web.actions import chia

setup_bp = Blueprint('setup', __name__)

@setup_bp.route('/setup', methods=['GET', 'POST'])
def setup():
    if globals.is_setup():
        return redirect(url_for('index')) # We haven't moved index yet, so it's still 'index'. 
        # Wait, if I keep index in routes.py (registered on app), it is available as 'index'.
    key_paths = globals.get_key_paths()
    current_app.logger.debug("Setup found these key paths: {0}".format(key_paths))
    show_setup = True
    if request.method == 'POST':
        if request.form.get('action') == 'generate':
            show_setup = not chia.generate_key(key_paths[0], globals.enabled_blockchains()[0])
        elif request.form.get('action') == 'import':
            show_setup = not chia.import_key(key_paths[0], request.form.get('mnemonic'), globals.enabled_blockchains()[0])
    [download_percentage, blockchain_download_size] = globals.blockchain_downloading()
    current_app.logger.info(_("Blockchain download") + f" @ {download_percentage}% - {blockchain_download_size}")
    if show_setup:
        return render_template('setup.html', key_paths = key_paths, 
            blockchain_download_size=blockchain_download_size, download_percentage=download_percentage)
    else:
        return redirect(url_for('index'))
