import unittest
from unittest.mock import MagicMock, patch
from AmazonSmartScraper.managers.proxy import ProxyManager

class TestProxyManager(unittest.TestCase):

    def setUp(self):
        self.logger = MagicMock()
        self.session = MagicMock()
        self.proxy_manager = ProxyManager(self.logger, self.session)


    @patch('requests.get')
    def test_validate_proxy(self, mock_get):
        # Mock the response for initial IP check
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "192.168.1.1"
        mock_get.return_value = mock_response

        # Validate proxy should return True
        self.proxy_manager.set_proxy('91.228.216.36',10047)
        result = self.proxy_manager._ProxyManager__validate_proxy()
        print(f"Initial IP check result: {result}")
        self.assertTrue(result)

        # Mock the response for new IP check
        mock_response.text = "192.168.1.2"
        mock_get.return_value = mock_response

        # Validate proxy should return True
        result = self.proxy_manager._ProxyManager__validate_proxy()
        print(f"New IP check result: {result}")
        self.assertTrue(result)

        # Mock the response for failed IP check
        mock_response.text = "192.168.1.1"
        mock_get.return_value = mock_response

        # Validate proxy should return False
        result = self.proxy_manager._ProxyManager__validate_proxy()
        print(f"Failed IP check result: {result}")
        self.assertFalse(result)
    def test_set_proxy(self):
        self.proxy_manager.set_proxy('proxyhost', 8080)
        expected_proxies = {
            "http": "http://proxyhost:8080",
            "https": "http://proxyhost:8080",
        }
        self.assertEqual(self.proxy_manager.get_proxy(), expected_proxies)

        self.proxy_manager.set_proxy('proxyhost', 8080, 'user', 'pass')
        expected_proxies = {
            "http": "http://user:pass@proxyhost:8080",
            "https": "http://user:pass@proxyhost:8080",
        }
        self.assertEqual(self.proxy_manager.get_proxy(), expected_proxies)

    @patch('AmazonSmartScraper.managers.proxy.ProxyManager._ProxyManager__validate_proxy', return_value=True)
    def test_update_proxy_valid(self, mock_validate_proxy):
        self.proxy_manager.set_proxy('proxyhost', 8080)
        self.session.proxies.update.reset_mock()  # Reset mock call history
        self.proxy_manager.update_proxy()
        self.session.proxies.update.assert_called_once_with(self.proxy_manager.get_proxy())
    @patch('AmazonSmartScraper.managers.proxy.ProxyManager._ProxyManager__validate_proxy', return_value=False)
    def test_update_proxy_invalid(self, mock_validate_proxy):
        self.proxy_manager.set_proxy('proxyhost', 8080)
        self.proxy_manager.update_proxy()
        self.session.proxies.update.assert_not_called()

if __name__ == '__main__':
    unittest.main()