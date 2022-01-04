"""Certificate endpoint handler"""
import logging

from flask import Blueprint, jsonify

from c8y_api.app import CumulocityApi

logger = logging.getLogger('Data Mailbox')
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

c8y = CumulocityApi()

bp = Blueprint('datamailbox', __name__)


@bp.route('/')
def datamailbox():
    """Data Mailbox Handler
    """
    logger.info('Data Mailbox endpoint is available.')

    dm = DataMailboxHandler()

    # Call all necessary methods for validating the device
    # dm.get_ewons()
    # dm.sync_data()

    return jsonify(datamailbox='running')


class DataMailboxHandler:

    def __init__(self):
        super()
        # self.device_id = device_id

    def get_ewons(self):
        print('get list of ewons...' )

    def sync_data(self):
        print('sync data...')

