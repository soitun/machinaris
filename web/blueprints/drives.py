from flask import Blueprint, render_template, request, make_response
from web.utils import get_lang
from common.config import globals
from web.actions import drives as d

drives_bp = Blueprint('drives', __name__)

@drives_bp.route('/drives', methods=['GET','POST'])
def index():
    if request.args.get('device') and request.args.get('hostname'):
        return make_response(d.load_smartctl_info(request.args.get('hostname'), request.args.get('device')), 200)
    if request.method == 'POST':
        if request.form.get('action') == 'remove':
            d.remove_selected_drives(request.form.getlist('unique_id'))
        elif request.form.get('action') == 'purge':
            d.remove_all_drives()
        else:
            d.save_settings(request.form)
    gc = globals.load()
    drvs = d.load_drive_summary()
    settings = d.load_settings()
    return render_template('drives.html', reload_seconds=120, 
        drives=drvs, settings=settings, global_config=gc, lang=get_lang(request))
