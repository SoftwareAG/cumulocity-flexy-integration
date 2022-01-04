"""loglevel handler to get and set the log level during runtime"""
import logging

from werkzeug.exceptions import HTTPException
from flask import Blueprint, jsonify, request
from cumulocity_flexy_integration.core import logger

bp = Blueprint('logger', __name__)

class InvalidLogLevel(HTTPException):
    """InvalidLogLevel Exception"""
    code = 500
    name = 'Invalid log level'
    description = 'Only DEBUG, INFO, WARNING and ERROR are accepted'


@bp.route('/loglevel', methods=['POST', 'GET'])
def health():
    """Get/set the log level

    POST: Expected body:
    {
        "level": "<DEBUG|INFO|WARNING|ERROR>"
    }
    """
    if request.method == 'POST':
        content = request.json
        if content and 'level' in content:
            nextLogLevel = content['level']
            logger.warning(
                f'Changing log level from {logging.getLevelName(logger.getEffectiveLevel())} to {nextLogLevel}')
            try:
                logger.setLevel(nextLogLevel)
            except ValueError as ex:
                logging.warning(f'Unknown log level. {ex}')
                raise InvalidLogLevel()

    return jsonify(level=logging.getLevelName(logger.getEffectiveLevel()))
