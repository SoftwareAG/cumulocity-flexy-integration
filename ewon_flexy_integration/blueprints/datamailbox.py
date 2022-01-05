"""Certificate endpoint handler"""
import json
import logging

from flask import Blueprint, jsonify, request
import requests

from c8y_api.app import CumulocityApi
from werkzeug.exceptions import HTTPException

logger = logging.getLogger('Data Mailbox')
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#c8y = CumulocityApi()

bp = Blueprint('datamailbox', __name__)

@bp.route('/hello')
def hello():
    """Hello endpoint
    """
    logger.info("Data Mailbox says 'hello'.")

    # Call all necessary methods for validating the device
    # dm.get_ewons()
    # dm.sync_data()

    return jsonify(datamailbox='hello')

@bp.route('/getewons')
def getewons():
    """Get list of EWON devices
    """
    logger.info("Request for ewon list...")
    logger.debug("request args = %s" % request.args)

    token = request.args.get('t2mtoken')
    dev_id = request.args.get('t2mdevid')
    logger.debug("request args token and devid = %s \t %s" % (token, dev_id))

    dm = DataMailboxHandler(token, dev_id)
    try:
        result = dm.get_ewons()
    except HTTPException as exception:
        return jsonify(exception)

    return jsonify(result)


class DataMailboxHandler:

    def __init__(self, token, dev_id):
        self.token = token
        self.dev_id = dev_id
        self.BASE_URL = 'https://data.talk2m.com'

    def get_ewons(self)->any:
        print('Get list of ewons...' )
        url_service = '/getewons'

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {"t2mdevid": self.dev_id, "t2mtoken": self.token}
        logger.debug("Send POST request to datamailbox: %s \t %s \t %s" % (self.BASE_URL + url_service, data, headers))
        r = requests.post(self.BASE_URL + url_service, data = data, headers = headers)
        
        json_body = r.text.splitlines()[-1]  
        json_data = json.loads(json_body)
        
        return json_data

    def sync_data(self):
        print('sync data...')

