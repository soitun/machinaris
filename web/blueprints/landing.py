from flask import Blueprint, render_template, redirect, url_for, request, current_app
from common.config import globals
from web.utils import get_lang
import random
import os

landing_bp = Blueprint('landing', __name__)

@landing_bp.route('/')
def landing():
    gc = globals.load()
    if not globals.is_setup():
        return redirect(url_for('setup.setup'))
    for accept in request.accept_languages.values():
        current_app.logger.info("ACCEPT IS {0}".format(accept))
    current_app.logger.info("LANGUAGES IS {0}".format(current_app.config['LANGUAGES']))
    lang = get_lang(request)
    
    # Need to handle path to static files correctly if cwd changes, but Flask handles it relative to app root usually.
    # Original code: open('web/static/landings/{0}.txt'...)
    # We should use os.path.join(current_app.root_path, 'static', 'landings', ...)
    
    landing_path = os.path.join(current_app.root_path, 'static', 'landings', '{0}.txt'.format(lang))
    
    # Fallback if specific lang not found? Original code just opened it contextually.
    if not os.path.exists(landing_path):
        landing_path = os.path.join(current_app.root_path, 'static', 'landings', 'en.txt') # Fallback
        
    try:
        msg = random.choice(list(open(landing_path)))
    except Exception as e:
        current_app.logger.error("Error reading landing txt: %s", e)
        msg = "Welcome to Machinaris!"

    if msg.endswith(".png"):
        msg = "<img style='height: 150px' src='{0}' />".format(url_for('static', filename='/landings/' + msg))
    return render_template('landing.html', random_message=msg)
