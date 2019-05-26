from unittest import TestCase

from ..base_api import BaseAPI


class TestBaseAPI(TestCase):
    def test_construction(self):
        """
        Test object construction.

        """
        base_api = BaseAPI('https://example.com/test/', 'asecretkey')
        self.assertEqual('https://example.com/test/', base_api.url)
        self.assertEqual('asecretkey', base_api.api_key)
