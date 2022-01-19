"""Certificate endpoint handler"""
from copy import copy, deepcopy
import json
import logging
from ewon_flexy_integration.models.c8y_ewon_flexy_integration import C8YEwonFlexyIntegration
from flask.wrappers import Response
import requests

from flask import Blueprint, jsonify, request

from c8y_api.app import CumulocityApp
from c8y_api.model import Measurement, ManagedObject

from werkzeug.exceptions import Conflict, HTTPException

from ewon_flexy_integration.utils.constants import C8Y_EXTERNAL_ID_PREFIX, C8Y_EXTERNAL_ID_TYPE, DM_BASE_URL, TALK2M_DEVELOPER_ID

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

    dm = DataMailboxHandler(token)
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
    job_id = request.args.get('jobId')
    tenant_id = request.args.get('tenantId')
    print("==========================================")
    print(tenant_id)
    c8y = CumulocityApp.get_tenant_instance(tenant_id)
    
    dm = DataMailboxHandler(token)
    c8y_ewon_integration = C8YEwonFlexyIntegration(c8y)
    ewon_ids = c8y_ewon_integration.get_ewons_from_job_id(job_id)

    # Go through list of ewon gateways
    for ewon_id in ewon_ids:
        try:
            dm_history:dict = dm.sync_data(ewon_id)
        except HTTPException as exception:
            return jsonify(exception)

        # Go through list of history and sync with c8y
        for ewon in dm_history["ewons"]:
            try:
                ewon_mo:ManagedObject = c8y_ewon_integration.get_ewon_device(str(ewon["id"]))
            except (KeyError) as error:
                continue

            # Each tag represents another measurement type
            tags: list = ewon["tags"]
            for t in tags:   
                
                try:
                    # Send numbers as measurements
                    if t.get("dataType") & ( t.get("dataType") == "Float" | t.get("dataType") == "Int"):
                        print("Start creating measurements...")
                        c8y_ewon_integration.create_measurements_history(t, ewon_mo.id, False)
                    # Send booleans as measurement
                    elif t.get("dataType") & ( t.get("dataType") == "Boolean"):
                        print("Start creating measurements, convert boolean to 0 and 1...")
                        c8y_ewon_integration.create_measurements_history(t, ewon_mo.id, True)
                    # Send strings as events
                    elif t.get("dataType") & ( t.get("dataType") == "String"):
                        print("Start creating events...")
                        logger.info("sending event to be defined.")
                    # Unknown data type
                    else:
                        logger.warn("Unknown data type for tag: %s" , t.get("dataType"))
                
                except (ValueError, TypeError, SyntaxError, KeyError) as error:
                    logger.error("failed post history to cumulocity: %s", error)
                    return Conflict("Failed post history to cumulocity: %s", error)

    return '', 200

class DataMailboxHandler:
    """ Handler for Data Mailbox
    """
    def __init__(self, token):
        """Init Handler

        Args:
            token (str): Token allows access to the Ewon gateways of one selected pool.
        """
        self.token = token
        self.dev_id = TALK2M_DEVELOPER_ID
        self.base_url = DM_BASE_URL

    def get_ewons(self)-> dict:
        """ This Service lists all Ewon gateways sending data to Data Mailbox. 

            Returns:
                Returns the list of Ewon gateways.
        """

        print('Get list of ewons...' )
        url_service = '/getewons'

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {"t2mdevid": self.dev_id, "t2mtoken": self.token}
        logger.debug("Send POST request to datamailbox: %s \t %s \t %s" % (self.base_url + url_service, data, headers))
        r = requests.post(self.base_url + url_service, data = data, headers = headers)
        
        json_body = r.text.splitlines()[-1]  
        json_data = json.loads(json_body)
        
        return json_data

    def sync_data(self, ewon_id: str, **kwargs ) -> dict:
        """ This Service retrieves all data of a Talk2M account incrementally. 
            Therefore, only new data is returned on each API request.

            Args:
                tenant_id (str):  ID of the tenant to get access to
                ewon_id (str): A comma separated list of Ewon gateway IDs.
                lastTransactionId (str):    ID of the transaction that was returned by the latest <syncdata> request.
                                            The system returns all the historical data that has been received by the DataMailbox since
                                            the last transaction and a new transaction ID. 

            Returns:
                Content of the DataMailbox: configuration, tag history and alarm history.
        """

        print('sync data...')
        url_service = '/syncdata'

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            "t2mdevid": self.dev_id, 
            "t2mtoken": self.token, 
            "ewonId": ewon_id,
            # "createTransaction" : True
            }
        lastTransactionId = kwargs.get('lastTransactionId', None)
        if lastTransactionId:
            data["lastTransactionId"] = lastTransactionId

        logger.debug("Send POST request to datamailbox: %s \t %s \t %s" % (self.base_url + url_service, data, headers))
        r = requests.post(self.base_url + url_service, data = data, headers = headers)

        json_body = r.text.splitlines()[-1]  
        json_data = json.loads(json_body)

        return json_data

