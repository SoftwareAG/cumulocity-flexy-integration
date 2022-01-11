"""Certificate endpoint handler"""
from copy import copy, deepcopy
import json
import logging
from flask.wrappers import Response
import requests

from flask import Blueprint, jsonify, request

from c8y_api.app import CumulocityApp
from c8y_api.model import Measurement, ManagedObject

from werkzeug.exceptions import Conflict, HTTPException

logger = logging.getLogger('Data Mailbox')
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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

    token = request.args.get('t2mtoken')
    dev_id = request.args.get('t2mdevid')

    dm = DataMailboxHandler(token, dev_id)
    try:
        result = dm.get_ewons()
    except HTTPException as exception:
        return jsonify(exception)

    return jsonify(result)

@bp.route('/syncdata')
def syncdata():
    """Get list of data from devices
    """
    logger.info("Get data from ewon device...")

    token = request.args.get('t2mtoken')
    dev_id = request.args.get('t2mdevid')
    ewon_id = request.args.get('ewonId')
    tenant_id = request.args.get('tenantId')
    print("==========================================")
    print(tenant_id)
    c8y = CumulocityApp.get_tenant_instance(tenant_id)
    
    dm = DataMailboxHandler(token, dev_id, ewon_id)
    try:
        result:dict = dm.get_data()
    except HTTPException as exception:
        return jsonify(exception)

    # Go through list of history and sync with c8y
    print("------")
    for ewon in result["ewons"]:
        tags: list = ewon["tags"]
        try:
            inventory:ManagedObject = c8y.identity.get_object("flexy_" + str(ewon["id"]),"flexy_id")
        except (KeyError) as error:
            continue

        # Each tag represents another measurement type
        measurements = []
        for t in tags:   
            # List of history values
            for h in t.get("history"):
                m = Measurement()
                m.type = 'c8y_Measurement'
                m.source = inventory.id
                m[t.get("name")] = { t.get("name").upper()[:1] : {'unit': '', 'value': float(h.get("value")) }}
                m.time = h.get("date")
                measurements.append( m )
        try:
            c8y.measurements.create(*measurements)
        except (ValueError, TypeError, SyntaxError, KeyError) as error:
            logger.error("failed post measurements: %s", error)
            return Conflict("Failed post measurements: %s", error)

    return '', 200

class DataMailboxHandler:

    def __init__(self, token, dev_id, ewon_id=''):
        self.token = token
        self.dev_id = dev_id
        self.ewon_id = ewon_id
        self.BASE_URL = 'https://data.talk2m.com'

    def get_ewons(self)-> dict:
        print('Get list of ewons...' )
        url_service = '/getewons'

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {"t2mdevid": self.dev_id, "t2mtoken": self.token}
        logger.debug("Send POST request to datamailbox: %s \t %s \t %s" % (self.BASE_URL + url_service, data, headers))
        r = requests.post(self.BASE_URL + url_service, data = data, headers = headers)
        
        json_body = r.text.splitlines()[-1]  
        json_data = json.loads(json_body)
        
        return json_data

    def get_data(self) -> dict:
        print('sync data...')
        url_service = '/syncdata'

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {"t2mdevid": self.dev_id, "t2mtoken": self.token, "ewonId": self.ewon_id}
        logger.debug("Send POST request to datamailbox: %s \t %s \t %s" % (self.BASE_URL + url_service, data, headers))
        r = requests.post(self.BASE_URL + url_service, data = data, headers = headers)

        json_body = r.text.splitlines()[-1]  
        json_data = json.loads(json_body)

        return json_data

