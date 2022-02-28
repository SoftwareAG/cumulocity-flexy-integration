"""Certificate endpoint handler"""
import json
import logging
import requests

from flask import Blueprint, jsonify, request
from werkzeug.exceptions import HTTPException
from ewon_flexy_integration.utils.constants import DM_BASE_URL, TALK2M_DEVELOPER_ID

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
    #dev_id = request.args.get('t2mdevid')

    dm_handler = DataMailboxHandler(token)
    try:
        result = dm_handler.get_ewons()
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

    def get_ewons(self) -> dict:
        """ This Service lists all Ewon gateways sending data to Data Mailbox.

            Returns:
                Returns the list of Ewon gateways.
        """

        print('Get list of ewons...')
        url_service = '/getewons'

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {"t2mdevid": self.dev_id, "t2mtoken": self.token}
        logger.debug("Send POST request to datamailbox: %s, %s, %s",
                     self.base_url + url_service, data, headers)
        r = requests.post(self.base_url + url_service,
                          data=data, headers=headers)

        json_body = r.text.splitlines()[-1]
        json_data = json.loads(json_body)

        return json_data

    def sync_data(self, ewon_id: str, last_transaction_id: int) -> dict:
        """ This Service retrieves all data of a Talk2M account incrementally. 
            Therefore, only new data is returned on each API request.

            Args:
                tenant_id (str):  ID of the tenant to get access to
                ewon_id (str): A comma separated list of Ewon gateway IDs.
                last_transaction_id (str):    ID of the transaction that was returned by the latest <syncdata> request.
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

        if last_transaction_id > 0:
            data["lastTransactionId"] = last_transaction_id

        logger.debug("Send POST request to datamailbox: %s, %s, %s",
                     self.base_url + url_service, data, headers)
        r = requests.post(self.base_url + url_service,
                          data=data, headers=headers)

        json_body = r.text.splitlines()[-1]
        json_data = json.loads(json_body)

        return json_data

    def sync_all_history_data(self, ewon_id: str, last_transaction_id: int) -> dict:
        """ This Service retrieves all data of a Talk2M account incrementally. 
                    Therefore, only new data is returned on each API request.

                    Args:
                        tenant_id (str):  ID of the tenant to get access to
                        ewon_id (str): A comma separated list of Ewon gateway IDs.
                        last_transaction_id (str):    ID of the transaction that was returned by the latest <syncdata> request.
                                                    The system returns all the historical data that has been received by the DataMailbox since
                                                    the last transaction and a new transaction ID. 

                    Returns:
                        Content of the DataMailbox: configuration, tag history and alarm history.
                """

        print('sync data...')
        json_data = None
        more_data_available: bool = True
        tags_list = []

        while more_data_available:
            data = self.sync_data(ewon_id, last_transaction_id)
            if len(data['ewons']) > 0:
                if json_data is None:
                    json_data = data
                    tags_list.extend(data['ewons'][0]['tags'])
                else:
                    if len(data['ewons'][0]['tags']) > 0:
                        tags = data['ewons'][0]['tags']
                        tags_list.extend(tags)
            more_data_available = data['moreDataAvailable'] if 'moreDataAvailable' in data else False
            last_transaction_id = int(data['transactionId'])

        tags_unified = dict()
        for tag in tags_list:
            if (tag['name'] in tags_unified):
                tag_history = tags_unified[tag['name']]
                tag_history['history'].extend(tag['history'])
                tags_unified[tag['name']] = tag_history
            else:
                tags_unified[tag['name']] = tag

        if len(data['ewons']) > 0 and len(tags_list) > 0:
            json_data['ewons'][0]['tags'] = []
            for key in tags_unified:
                json_data['ewons'][0]['tags'].append(tags_unified.get(key))
            json_data['transactionId'] = last_transaction_id
            json_data['moreDataAvailable'] = more_data_available

        return json_data