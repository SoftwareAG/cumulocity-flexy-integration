"""Check files if exist on given url"""
from flask import Blueprint, jsonify, request
import requests
import validators

bp = Blueprint('agent_release', __name__)

@bp.route('/checkFiles')
def check_files():
    """check files endpoint
    """
    base_url = request.headers.get('filesUrl')
    files_exist = False
    if (base_url is not None):
        validation_result = validators.url(base_url)
        if (validation_result):
            response_jar = requests.get(
                base_url + "/flexy-cumulocity-connector-1.0.3-full.jar")
            response_jvm = requests.head(base_url + "/jvmrun")
            response_zip = requests.head(
                base_url + "/flexy-cumulocity-connector-1.0.3.zip")
            files_exist = response_zip.status_code != 404 and response_jar.status_code != 404 and response_jvm.status_code != 404 and response_zip.status_code != 500 and response_jar.status_code != 500 and response_jvm.status_code != 500
    return jsonify(files_exist)