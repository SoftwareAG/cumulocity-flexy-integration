
from flask import Blueprint, jsonify, request
import requests

bp = Blueprint('agent_release', __name__)


@bp.route('/checkFiles')
def check_files():
    """check files endpoint
    """
    url = request.headers.get('filesUrl')
    response_jar = requests.get(
        url + "/flexy-cumulocity-connector-1.0.3-full.jar")
    response_jvm = requests.head(url + "/jvmrun")
    response_zip = requests.head(url + "/flexy-cumulocity-connector-1.0.3.zip")
    files_exist = response_zip.status_code != 404 and response_jar.status_code != 404 and response_jvm.status_code != 404 and response_zip.status_code != 500 and response_jar.status_code != 500 and response_jvm.status_code != 500
    return jsonify(files_exist)
