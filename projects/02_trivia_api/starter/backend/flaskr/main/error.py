from flask import jsonify

from . import main as app


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": 404,
        "message": "Not found"
    }), 404


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "error": 500,
        "message": "Internal Server Error"
    }), 500


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "error": 400,
        "message": "Bad Request"
    }), 400


@app.errorhandler(422)
def unprocessable_entity(error):
    return jsonify({
        "error": 422,
        "message": "Unprocessable Entity"
    }), 422
