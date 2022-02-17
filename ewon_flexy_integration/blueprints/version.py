"""Metric handler"""
import json
from flask import Blueprint
from ewon_flexy_integration._version import get_versions

bp = Blueprint('version', __name__)

@bp.route('/version')
def version():
    """Get microservice version information
    """
    return json.dumps(get_versions())
