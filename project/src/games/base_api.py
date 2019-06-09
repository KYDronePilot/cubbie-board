"""
For holding base API class used in more specific API classes.

"""

import requests
from requests.adapters import HTTPAdapter
from typing import Dict, Union, Any


class BaseAPI(object):
    """
    The base API class used by more specific API classes.

    Attributes:
        url (str): The API URL
        api_key (str): The API auth key

    """

    def __init__(self, url, api_key):
        # type: (str, str) -> None
        """
        Set the API info.

        Args:
            url (str): The API URL
            api_key (str): The API auth key

        """
        self.url = url  # type: str
        self.api_key = api_key  # type: str

    @staticmethod
    def post_request_wrapper(url, data, headers):
        # type: (str, Dict[str, Union[int, str]], Dict[str, Union[int, str]]) -> Any
        """
        A post request wrapper for allowing infinite retries.

        Args:
            url (str): URL to send request to
            data (Dict[str, Union[int, str]]): Request data
            headers (Dict[str, Union[int, str]]): Request headers

        Returns:
            Any: The requests response

        """
        # Continually make requests until it goes through.
        while True:
            # Get a session with a set amount of retries.
            session = requests.Session()
            session.mount(url, HTTPAdapter(max_retries=4))
            # Make the request, catching errors.
            try:
                return session.post(
                    url,
                    data=data,
                    headers=headers
                )
            except Exception as e:
                print(e)
