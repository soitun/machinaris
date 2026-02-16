from flask import Blueprint, render_template, redirect, url_for, request, make_response
from flask_babel import _
from markupsafe import escape
from common.config import globals
from web.actions import plotman, worker, stats, chia
from web.utils import get_lang, find_selected_worker

plotting_bp = Blueprint('plotting', __name__)

@plotting_bp.route('/plotting/jobs', methods=['GET', 'POST'])
def jobs():
    gc = globals.load()
    if request.method == 'POST':
        if request.form.get('action') == 'start':
            hostname= request.form.get('hostname')
            blockchain = request.form.get('blockchain')
            plotter = worker.get_worker(hostname, blockchain)
            if request.form.get('service') == 'plotting':
                plotman.start_plotman(plotter)
        elif request.form.get('action') == 'stop':
            hostname= request.form.get('hostname')
            blockchain = request.form.get('blockchain')
            plotter = worker.get_worker(hostname, blockchain)
            if request.form.get('service') == 'plotting':
                plotman.stop_plotman(plotter)
        elif request.form.get('action') in ['suspend', 'resume', 'kill']:
            action = request.form.get('action')
            plot_ids = request.form.getlist('plot_id')
            plotman.action_plots(action, plot_ids)
        elif request.form.get('action') == 'schedule':
            schedules = request.form.getlist('schedules')
            plotman.save_schedules(schedules)
        else:
            # app.logger not available directly, use globals or current_app? 
            # Flask blueprints can access current_app
            pass 
        return redirect(url_for('plotting.jobs')) # Force a redirect to allow time to update status
    plotters = plotman.load_plotters()
    plotting = plotman.load_plotting_summary()
    job_stats = stats.load_plotting_stats()
    return render_template('plotting/jobs.html', reload_seconds=120,  plotting=plotting, 
        plotters=plotters, job_stats=job_stats, global_config=gc, lang=get_lang(request))

@plotting_bp.route('/plotting/transfers', methods=['GET', 'POST'])
def transfers():
    gc = globals.load()
    if request.method == 'POST':
        if request.form.get('action') == 'start':
            hostname= request.form.get('hostname')
            blockchain = request.form.get('blockchain')
            plotter = worker.get_worker(hostname, blockchain)
            if request.form.get('service') == 'archiving':
                plotman.start_archiving(plotter)
        elif request.form.get('action') == 'stop':
            hostname= request.form.get('hostname')
            blockchain = request.form.get('blockchain')
            plotter = worker.get_worker(hostname, blockchain)
            if request.form.get('service') == 'archiving':
                plotman.stop_archiving(plotter)
        return redirect(url_for('plotting.transfers')) # Force a redirect to allow time to update status
    plotters = plotman.load_plotters()
    transfers = plotman.load_archiving_summary()
    disk_usage = stats.load_current_disk_usage('plots')
    farmers = chia.load_farmers()
    stats.set_disk_usage_per_farmer(farmers, disk_usage)
    return render_template('plotting/transfers.html', plotters=plotters, farmers=farmers, transfers=transfers, 
        disk_usage=disk_usage, global_config=gc, lang=get_lang(request), reload_seconds=120)

@plotting_bp.route('/plotting/workers')
def workers():
    gc = globals.load()
    plotters = plotman.load_plotters()
    disk_usage = stats.load_recent_disk_usage('plotting')
    mem_usage = stats.load_recent_mem_usage('plotting')
    return render_template('plotting/workers.html', plotters=plotters, 
        disk_usage=disk_usage, mem_usage=mem_usage, global_config=gc, lang=get_lang(request))

@plotting_bp.route('/settings/plotting', methods=['GET', 'POST'])
def settings():
    selected_worker_hostname = None
    blockchains = globals.enabled_blockchains()
    selected_blockchain = None
    gc = globals.load()
    if request.method == 'POST':
        selected_worker_hostname = request.form.get('worker')
        selected_blockchain = request.form.get('blockchain')
        if request.form.get('type') == 'schedule':
            # app.logger.info('Saving updated plotting schedule for worker: {0}'.format(selected_worker_hostname))
            plotman.save_schedules(worker.get_worker(selected_worker_hostname, selected_blockchain), selected_blockchain, request.form.get('schedules'))
            return make_response("Successfully saved {0} plotting schedule on {1}.".format(escape(selected_worker_hostname), escape(selected_blockchain)), 200)
        else: #
            plotman.save_config(worker.get_worker(selected_worker_hostname, selected_blockchain), selected_blockchain, request.form.get("config"))
    workers_summary = worker.load_worker_summary()
    selected_worker = find_selected_worker(workers_summary.plotters(), selected_worker_hostname, selected_blockchain)
    if not selected_blockchain:
        selected_blockchain = selected_worker['blockchain']
    return render_template('settings/plotting.html', blockchains=blockchains, selected_blockchain=selected_blockchain,
        workers=workers_summary.plotters, selected_worker=selected_worker['hostname'], global_config=gc)
