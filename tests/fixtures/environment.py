"""Flexy test device fixture"""

from threading import Lock
from typing import List

from c8y_api.app import CumulocityApi
from c8y_api.model.inventory import Fragment, ManagedObject


class EnvironmentFixture:
    """Setup fixture to be used generate test managed objects in Cumulocity
    """
    def __init__(self, api: CumulocityApi) -> None:
        self._api = api
        assert self._api
        self._lock = Lock()
        self._managed_objects: List[str] = []

    # def create_gateway(self, name: str, *fragments: Fragment) -> ManagedObject:
    #     """Create a gateway managed object

    #     Returns:
    #         ManagedObject: New managed object
    #     """
    #     mo = ManagedObject(self._api, name=name)
    #     mo['c8y_IsDevice'] = {}
    #     if len(fragments):
    #         mo.add_fragments(list(fragments))
    #     c_mo = mo.create()

    #     if c_mo:
    #         self._save_mo(c_mo)

    #     return c_mo
    
    def _save_mo(self, mo: ManagedObject) -> None:
        """Save the managed object for cleanup later

        Args:
            mo (ManagedObject): Managed object
        """
        with self._lock:
            self._managed_objects.append(mo.id)
        

    def cleanup(self) -> None:
        """Cleanup any managed objects created by the fixture
        """
        for mo in self._managed_objects:
            self._api.inventory.delete(mo)
