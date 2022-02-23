"""Implementing REST calls to Cumulocity """
import logging
import urllib.parse
from typing import Dict, Any, List
from c8y_api.app import CumulocityApi

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class InventoryApi:
    """Extend inventory to include additional methods"""

    def __init__(self, c8y: CumulocityApi):
        """

        Args:
            c8y (CumulocityApi): [description]
        """
        self.c8y = c8y

    def _encode_filter(self, params: Dict[str, Any]) -> str:
        """Create url filter from dictionary structure

        Args:
            params (Dict[str, Any]): Filter attributes

        Returns:
            str: Filter url
        """

        encoded = f'{urllib.parse.urlencode(params)}'
        return encoded

    def get_by_query(self, type_: str = '', fragment: str = '',
                     query: str = '', page_size='', sort: str = '',
                     desc: bool = True) -> List[Dict[str, any]]:
        """Fetches by query

        Args:
            type (str, optional): type of managed object. Defaults to ''.
            fragment (str, optional): fragment to query with. Defaults to ''.
            query (str, optional): explicit querying. Defaults to ''.
            page_size (str, optional): query by page_size. Defaults to ''.
            sort (str, optional): order by an attribute. Defaults to ''.
            desc (bool, optional): ascending or descending. Defaults to True.

        Returns:
            List[Dict[str, any]]: list of managed objects satisfying above conditions
        """
        def set_asc_or_desc_for_sort(sort_by: str, desc: bool):
            """set orderBy to asc or desc

            Args:
                sortBy (str): attribute to sort_by
                desc (bool): is descending if True else ascending
            """
            def is_asc_or_desc(desc: bool):
                return ' desc' if desc else ' asc'
            if sort_by:
                return f'{sort_by}' + is_asc_or_desc(desc)

        def set_type_in_query_if_exists(type_: str):
            """returns query part containing type

            Returns:
                str: query portion containing type
            """
            return f'type eq {type_}' if type_ else ''

        try:
            filter_query = f'$filter=({query}' + set_type_in_query_if_exists(type_) + ')$orderby=' + \
                set_asc_or_desc_for_sort(sort, desc)

            params_dict = {'fragment': fragment,
                           'query': filter_query, 'pageSize': page_size}

            query_params = {k: v for k, v in params_dict.items() if v}
            url_query = self._encode_filter(query_params)

            logger.info('url_query: %s', url_query)

            return self.c8y.get(f'/inventory/managedObjects?{url_query}')['managedObjects']
        except TypeError as ex:
            logger.info('could not update url query. exception=%s', ex)

        return None


class DeviceControlAPI:
    """Cumulocity Device Control API"""

    def __init__(self, c8y: CumulocityApi):
        """

        Args:
            c8y (CumulocityApi): [description]
        """
        self.c8y = c8y

    def get(self, operation_id: str) -> Dict[str, Any]:
        """Get operation by id

        Args:
            operation_id (str): Operation id

        Returns:
            Dict[str, Any]: Operation as a dictionary
        """
        try:
            return self.c8y.get(f'/devicecontrol/operations/{operation_id}')
        except Exception as ex:
            logger.error(
                'could not fetch the request operation. exception=%s', ex)


class TenantApi:
    """Cumulocity tenant API"""

    def __init__(self, c8y: CumulocityApi):
        """
        Args:
            c8y (CumulocityApi): [description]
        """
        self.c8y = c8y

    def get_system_version(self):
        """Get system version"""
        try:
            val = self.c8y.get(
                '/tenant/system/options/system/version')
            logger.info('tenant system version: %s', val['value'])
            # tenant/system/options/system/version
            return val['value']
        except Exception as ex:
            logger.error(
                'could not fetch the system version. exception=%s', ex)

    def get_tenant_option(self, category, key):
        """Get tenant option value by key and category"""
        try:
            uri = f'/tenant/options/{category}/{key}'
            val = self.c8y.get(uri)
            return val['value']
        except Exception as ex:
            logger.error(
                'could not fetch the Tenant Option. exception=%s', ex)