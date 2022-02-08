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

    def sync_data(self, ewon_id: str, lastTransactionId: int, **kwargs ) -> dict:
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
        url_service = '/syncdata'

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            "t2mdevid": self.dev_id, 
            "t2mtoken": self.token, 
            "ewonId": ewon_id,
            "createTransaction": True
            }
            
        if lastTransactionId > 0:
            data["lastTransactionId"] = lastTransactionId

        logger.debug("Send POST request to datamailbox: %s \t %s \t %s" % (self.base_url + url_service, data, headers))
        r = requests.post(self.base_url + url_service, data = data, headers = headers)

        json_body = r.text.splitlines()[-1]  
        json_data = json.loads(json_body)

        return json_data

    def sync_all_history_data(self, ewon_id: str, lastTransactionId: int, **kwargs ) -> dict:
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
        json_data: dict = None
        more_data_available:bool = True
        tags_list = []
        while more_data_available:
            data = self.sync_data(ewon_id, lastTransactionId)
            if json_data is None:
                json_data = data
            else:
                if len(data['ewons']) > 0 & len(data['ewons'][0]['tags']):
                    tags = data['ewons'][0]['tags']
                    tags_list.extend(tags)
            more_data_available = data['moreDataAvailable'] if 'moreDataAvailable' in data else False
            lastTransactionId = int(data['transactionId'])
        
        json_data['ewons'][0]['tags'].extend(tags_list)
        json_data['transactionId'] = lastTransactionId
        json_data['moreDataAvailable'] = more_data_available

        return json_data

