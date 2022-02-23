"""Health handler"""
from flask import Blueprint, jsonify

bp = Blueprint('health', __name__)

@bp.route('/health')
def health():
    """Verify the status of the microservice
    """
    return jsonify(status='UP')
