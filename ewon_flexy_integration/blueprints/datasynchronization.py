"""Scheduler for historic data synchronization"""
import os
import logging
import base64
from urllib import response
import requests
from ewon_flexy_integration.utils.rest import TenantApi
from http.client import CONFLICT, HTTPException
from ewon_flexy_integration.blueprints.datamailbox import DataMailboxHandler
from ewon_flexy_integration.models.c8y_ewon_flexy_integration import C8YEwonFlexyIntegration
from c8y_api.model import ManagedObject
from flask import Blueprint, jsonify, request
from c8y_api.app import CumulocityApp

bp = Blueprint('datasynchronization', __name__)
logger = logging.getLogger('data synchronization')


@bp.route('/checkFiles')
def check_files():
    """check files endpoint
    """
    url = request.headers.get('filesUrl')
    
    responseJar = requests.head(url + "/flexy-cumulocity-connector-1.0.3-full.jar")
    responseJvm = requests.head(url + "/jvmrun1")
    responseZip = requests.head(url + "/flexy-cumulocity-connector-1.0.3.zip")
    
    filesExist = responseZip.status_code != '404' and responseJar.status_code != '404' and responseJvm.status_code != '404'

    return jsonify(filesExist)

@bp.route('/executalljobs')
def execute_all_jobs():
    """Manually execute synchronization of all jobs via this endpoint.
    """
    dsh_handler = DataSynchronizationHandler()
    total_jobs_executed = dsh_handler.synchronize_historic_data()
    result_message = "Total jobs executed: " + str(total_jobs_executed)
    logger.info(result_message)
    return result_message


@bp.route("/executejob")
def execute_job():
    """Manually execute synchronization for specific job via this endpoint.
    """
    token = request.headers.get('t2mtoken')
    job_id = request.headers.get('jobId')
    tenant_id = request.headers.get('tenantId')
    dsh_handler = DataSynchronizationHandler()
    return dsh_handler.syncdata(token, job_id, tenant_id)


class DataSynchronizationHandler:
    """Contains methods for syncrhonizing history data
    """

    def __init__(self):
        print(os.getenv('C8Y_BOOTSTRAP_TENANT'))
        self.c8y = CumulocityApp(os.getenv('C8Y_BOOTSTRAP_TENANT'))

    def synchronize_historic_data(self):
        """Synchronize history data according to jobs. 
        """
        subscribed_tenants_list = self.get_subscribed_tenants_list()
        jobs_executed = 0
        if (len(subscribed_tenants_list) > 0):
            for subscribed_tenant in subscribed_tenants_list:
                subscribed_tenant_id = subscribed_tenant["tenant"]
                subtenant_instance = self.c8y.get_tenant_instance(
                    subscribed_tenant_id)
                subtenant_response = subtenant_instance.get(
                    "/inventory/managedObjects?pageSize=100&fragmentType=c8y_HMSOnloadingJob&currentPage=1&withTotalPages=true")
                subtenant_jobs_mo_list = subtenant_response["managedObjects"]
                for job_mo in subtenant_jobs_mo_list:
                    if (job_mo["isActive"]):
                        owner = job_mo["owner"]
                        category = self.create_tenant_option_category(owner)
                        token = self.get_token_value_from_tenant_options(
                            category, subtenant_instance)
                        job_id = job_mo["id"]
                        if token is None:
                            logger.warning(
                                'Datamailbox token is missing in tenant options for user %s & job %s', owner, job_id)
                        else:
                            self.syncdata(token, job_id, subscribed_tenant_id)
                            jobs_executed = jobs_executed + 1
        return jobs_executed

    def create_tenant_option_category(self, string_to_encode: str):
        """_summary_

        Args:
            string_to_encode (str): _description_

        Returns:
            _type_: _description_
        """
        conversion_bytes = string_to_encode.encode('ascii')
        base64_bytes = base64.b64encode(conversion_bytes)
        converted = base64_bytes.decode('ascii')
        tenant_option_category = 'flexy_' + \
            converted.replace('=', '').replace('+', '-').replace('/', '_')
        return tenant_option_category

    def get_token_value_from_tenant_options(self, category, subtenant_instance):
        """_summary_

        Args:
            category (_type_): _description_
            subtenant_instance (_type_): _description_

        Returns:
            _type_: _description_
        """
        #c8y = CumulocityApp(os.getenv('C8Y_BOOTSTRAP_TENANT'))
        tenant_api = TenantApi(subtenant_instance)
        token = tenant_api.get_tenant_option(category, "token")
        return token

    def syncdata(self, token, job_id, tenant_id):
        """Get list of data from devices
        """
        logger.info('Executing Job: %s', job_id)
        tenant_instance = self.c8y.get_tenant_instance(tenant_id)

        dm_handler = DataMailboxHandler(token)
        c8y_ewon_integration = C8YEwonFlexyIntegration(tenant_instance)
        ewon_ids = c8y_ewon_integration.get_ewons_from_job_id(job_id)

        # Go through list of ewon gateways
        for ewon_id in ewon_ids:
            try:
                ewon_mo: ManagedObject = c8y_ewon_integration.get_ewon_device(
                    str(ewon_id))
            except KeyError:
                continue

            last_transaction_id: int
            try:
                if hasattr(ewon_mo, 'lastTransactionId'):
                    last_transaction_id = int(ewon_mo['lastTransactionId'])
            except KeyError:
                last_transaction_id = 0

            try:
                dm_history: dict = dm_handler.sync_all_history_data(
                    ewon_id, last_transaction_id)
            except HTTPException as exception:
                return jsonify(exception)

            if (dm_history is not None and len(dm_history["ewons"]) > 0):
                # Go through list of history and sync with c8y
                for ewon in dm_history["ewons"]:
                    logger.info(
                        "Synchronizing data for device: %s [%s]", ewon_mo.name, ewon_mo.id)
                    # Each tag represents another measurement type
                    tags: list = ewon["tags"]
                    for t in tags:
                        try:
                            logger.info("Posting measurements for Tag [%s], Datatype [%s], Count [%s]", t.get(
                                'name'), t.get('dataType'), len(t.get('history')))
                            if t.get("dataType"):
                                # Send numbers as measurements
                                if t.get("dataType") == 'Int':
                                    logger.info(
                                        "Start creating measurements...")
                                    c8y_ewon_integration.create_measurements_history(
                                        t, ewon_mo.id, False)
                                elif t.get("dataType") == 'Float':
                                    logger.info(
                                        "Start creating measurements...")
                                    c8y_ewon_integration.create_measurements_history(
                                        t, ewon_mo.id, False)
                                # Send booleans as measurement
                                elif t.get("dataType") == "Bool":
                                    logger.info(
                                        "Start creating measurements, convert boolean to 0 and 1...")
                                    c8y_ewon_integration.create_measurements_history(
                                        t, ewon_mo.id, True)
                                # Send strings as events
                                elif t.get("dataType") == "String":
                                    logger.info("Start creating events...")
                                    logger.info("sending event to be defined.")
                                # Unknown data type
                                else:
                                    logger.warning(
                                        "Unknown data type for tag: %s", t.get("dataType"))
                        except (ValueError, TypeError, SyntaxError, KeyError) as error:
                            logger.error(
                                "failed post history to cumulocity: %s", error)
                            return ("Failed post history to cumulocity: %s", error), CONFLICT
                    # Update lastTransactionId in Ewon Managed Object
                    last_transaction_id = dm_history['transactionId']
                    to_update = dict()
                    to_update["lastTransactionId"] = last_transaction_id
                    tenant_instance.put(
                        f'/inventory/managedObjects/{ewon_mo.id}', to_update)
                    logger.info(
                        "Successful Synchronization of data for device: %s [%s] till transaction [%s]", ewon_mo.name, ewon_mo.id, last_transaction_id)
            else:
                #logger.info(f"No new data found for device: {ewon_mo.name} [{ewon_mo.id}]")
                logger.info(
                    "No new data found for device %s [%s]:", ewon_mo.name, ewon_mo.id)
                if last_transaction_id is not None:
                    logger.info(
                        "History data is synchronized till last transaction [%s]", last_transaction_id)
        return '', 200

    def get_subscribed_tenants_list(self):
        """Fetch service users list of all subtenants
        """
        subscribed_tenants_list = []
        base_url = os.getenv('C8Y_BASEURL')
        boot_tenant_id = os.getenv('C8Y_BOOTSTRAP_TENANT')
        boot_user = os.getenv('C8Y_BOOTSTRAP_USER')
        boot_password = os.getenv('C8Y_BOOTSTRAP_PASSWORD')

        bootstrap_auth = self.build_auth(
            boot_tenant_id, boot_user, boot_password)

        response = requests.get(
            base_url + '/application/currentApplication/subscriptions', auth=bootstrap_auth)

        if response.json()['users']:
            subscribed_tenants_list = response.json()['users']
        return subscribed_tenants_list

    def build_auth(self, tenant_id, user, password):
        """Create auth string
        """
        return f'{tenant_id}/{user}', password
