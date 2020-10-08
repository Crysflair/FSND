
from flask import render_template
from . import rt


@rt.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@rt.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

@rt.errorhandler(405)
def not_found_error(error):
    return render_template('errors/405.html'), 405

@rt.errorhandler(500)
def not_found_error(error):
    return render_template('errors/500.html'), 500