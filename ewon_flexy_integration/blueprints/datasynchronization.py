"""Scheduler for historic data synchronization"""
import os
import logging
import requests
from http.client import CONFLICT, HTTPException
from ewon_flexy_integration.blueprints.datamailbox import DataMailboxHandler
from ewon_flexy_integration.models.c8y_ewon_flexy_integration import C8YEwonFlexyIntegration
from c8y_api.model import Measurement, ManagedObject

from flask import Blueprint, jsonify, request
from c8y_api.app import CumulocityApp

bp = Blueprint('datasynchronization', __name__)
logger = logging.getLogger('data synchronization')


@bp.route('/executalljobs')
def execute_all_jobs():
    """Manually execute synchronization of all jobs via this endpoint.
    """
    ##TODO store token in tenant options
    token = "53edRmx8AACZNyWiMSPpk9JMWy7YMTjQrjVIZ3as79Uiw444nA"
    dsh = DataSynchronizationHandler()
    total_jobs_executed = dsh.synchronize_historic_data(token)
    return "Total jobs executed: " + total_jobs_executed


@bp.route('/executejob')
def execute_job():
    """Manually execute synchronization for specific job via this endpoint.
    """
    ##TODO store token in tenant options
    token = "53edRmx8AACZNyWiMSPpk9JMWy7YMTjQrjVIZ3as79Uiw444nA"
    job_id = request.headers.get('jobId')
    tenant_id = request.headers.get('tenantId')
    dsh = DataSynchronizationHandler()
    return dsh.syncdata(token, job_id, tenant_id)


class DataSynchronizationHandler:

    def __init__(self):
        self.c8y = CumulocityApp()

    def synchronize_historic_data(self, token):
        """Synchronize history data according to jobs. 
        """
        subscribed_tenants_list = self.get_subscribed_tenants_list()
        if (len(subscribed_tenants_list) > 0):
            for subscribed_tenant in subscribed_tenants_list:
                subscribed_tenant_id = subscribed_tenant["tenant"]
                subtenant_instance = self.c8y.get_tenant_instance(
                    subscribed_tenant_id)
                subtenant_response = subtenant_instance.get(
                    "/inventory/managedObjects?pageSize=100&fragmentType=c8y_HMSOnloadingJob&currentPage=1&withTotalPages=true")
                subtenant_jobs_mo_list = subtenant_response["managedObjects"]
                jobs_executed = []
                for job_mo in subtenant_jobs_mo_list:
                    if (job_mo["isActive"]):
                        job_id = job_mo["id"]
                        self.syncdata(token, job_id, subscribed_tenant_id)
                        jobs_executed.append(job_mo)
        return len(jobs_executed)

    def syncdata(self, token, job_id, tenant_id):
        """Get list of data from devices
        """
        logger.info(f'Executing Job: {job_id}')
        c8y = self.c8y.get_tenant_instance(tenant_id)

        dm = DataMailboxHandler(token)
        c8y_ewon_integration = C8YEwonFlexyIntegration(c8y)
        ewon_ids = c8y_ewon_integration.get_ewons_from_job_id(job_id)

        # Go through list of ewon gateways
        for ewon_id in ewon_ids:
            try:
                dm_history: dict = dm.sync_data(ewon_id)
            except HTTPException as exception:
                return jsonify(exception)

            # Go through list of history and sync with c8y
            for ewon in dm_history["ewons"]:
                try:
                    ewon_mo: ManagedObject = c8y_ewon_integration.get_ewon_device(
                        str(ewon["id"]))
                except (KeyError) as error:
                    continue

                logger.info(
                    "Synchronizing data for device: {ewon_mo.name} [{ewon_mo.id}]")
                # Each tag represents another measurement type
                tags: list = ewon["tags"]
                for t in tags:
                    try:
                        # Send numbers as measurements
                        if t.get("dataType") & (t.get("dataType") == "Float" | t.get("dataType") == "Int"):
                            logger.info("Start creating measurements...")
                            c8y_ewon_integration.create_measurements_history(
                                t, ewon_mo.id, False)
                        # Send booleans as measurement
                        elif t.get("dataType") & (t.get("dataType") == "Boolean"):
                            logger.info(
                                "Start creating measurements, convert boolean to 0 and 1...")
                            c8y_ewon_integration.create_measurements_history(
                                t, ewon_mo.id, True)
                        # Send strings as events
                        elif t.get("dataType") & (t.get("dataType") == "String"):
                            logger.info("Start creating events...")
                            logger.info("sending event to be defined.")
                        # Unknown data type
                        else:
                            logger.warn(
                                "Unknown data type for tag: %s", t.get("dataType"))

                    except (ValueError, TypeError, SyntaxError, KeyError) as error:
                        logger.error(
                            "failed post history to cumulocity: %s", error)
                        return CONFLICT("Failed post history to cumulocity: %s", error)

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

        logger.info("get subscriptions: %s", response.json())

        if response.json()['users']:
            subscribed_tenants_list = response.json()['users']
        return subscribed_tenants_list

    def build_auth(self, tenant_id, user, password):
        """Create auth string
        """
        return f'{tenant_id}/{user}', password
