

from c8y_api.app import CumulocityApp
from c8y_api.model.managedobjects import Device, ManagedObject
from c8y_api.model.measurements import Measurement
from ewon_flexy_integration.utils.constants import C8Y_EXTERNAL_ID_PREFIX, C8Y_EXTERNAL_ID_TYPE


class C8YEwonFlexyIntegration:
    """ Handler to communicate with the c8y instance
    """
    def __init__(self, c8y: CumulocityApp):
        self.c8y = c8y

    def get_ewons_from_job_id(self, job_id: str) -> list:
        """Request for managed object to get list of Ewon gateways.

        Args:
            job_id (str): Managed Object id to request.

        Returns:
            list: List of Ewon gateways.
        """
        job_mo : ManagedObject = self.c8y.inventory.get(job_id)

        if hasattr(job_mo, 'ewons'):
            return job_mo.ewons
        else:
            return []

    def get_ewon_device(self, ewon_id: str) -> ManagedObject:
        """Get device object with external id.

        Args:
            ewon_id (str): Ewon Id from Talk2M

        Returns:
            ManagedObject: Ewon gateway device.

        """
        return self.c8y.identity.get_object(C8Y_EXTERNAL_ID_PREFIX + ewon_id + C8Y_EXTERNAL_ID_TYPE)

    def create_measurements_history(self, tag: any, source: str, isBoolean: bool) -> None:
        """Create Measurement history tag values

        Args:
            tag (any): Tag entry from Data Mailbox
            source (str): Source Id to publish measurements
        """
        # List of history values
        measurements = []
        for h in tag.get("history"):
            m = Measurement()
            m.type = 'c8y_Measurement'
            m.source = source
            m[tag.get("name")] = { tag.get("name").upper()[:1] : {'unit': '', 'value': 0.0 if h.get("value") == False else 1.0 }} \
                                    if isBoolean else { tag.get("name").upper()[:1] : {'unit': '', 'value': float(h.get("value")) }}
            m.time = h.get("date")
            measurements.append( m )
        # Send history measurements
        self.c8y.measurements.create(*measurements)
        
    