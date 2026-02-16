from flask import Blueprint, render_template, request, flash, current_app
from flask_babel import _
from web.utils import get_lang
from common.config import globals
from web.actions import chia, worker, mapping

connections_bp = Blueprint('connections', __name__)

@connections_bp.route('/connections', methods=['GET', 'POST'])
def index():
    gc = globals.load()
    selected_blockchain = worker.default_blockchain()
    if request.method == 'POST':
        if request.form.get('maxmind_account'):
            mapping.save_settings(request.form.get('maxmind_account'), request.form.get('maxmind_license_key'), request.form.get('mapbox_access_token'))
            flash(_("Saved mapping settings.  Please allow 10 minutes to generate location information for the map."), 'success')
        else:
            selected_blockchain = request.form.get('blockchain')
            if request.form.get('action') == "add":
                conns_to_add = []  # Empty list will use ATB peers list pull
                if request.form.get("connection"):
                    conns_to_add.add(request.form.get("connection"))
                chia.add_connections(conns_to_add, request.form.get('hostname'), request.form.get('blockchain'))
            elif request.form.get('action') == 'remove':
                chia.remove_connection(request.form.getlist('nodeid'), request.form.get('hostname'), request.form.get('blockchain'))
            else:
                current_app.logger.info(_("Unknown form action") + ": {0}".format(request.form))
    connections = chia.load_connections(lang=get_lang(request))
    return render_template('connections.html', reload_seconds=120, selected_blockchain = selected_blockchain,
        maxmind_license = mapping.load_maxmind_license(), mapbox_license = mapping.load_mapbox_license(), marker_hues=mapping.generate_marker_hues(connections),
        connections=connections, global_config=gc, lang=get_lang(request))
