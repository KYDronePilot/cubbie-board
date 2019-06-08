"""
For holding base API class used in more specific API classes.

"""


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
