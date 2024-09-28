import requests

class ProxyManager:
    """
    Manages proxy settings and validation for HTTP requests.
    """

    def __init__(self, logger, session):
        """
        Initializes the ProxyManager with a logger and a session.

        :param logger: Logger instance for logging information and errors.
        :param session: Session instance for making HTTP requests.
        """
        self.__logger = logger
        self.session = session
        self.__proxies = {}

    def __validate_proxy(self) -> bool:
        """
        Validates the current proxy settings by making a request to a test URL.

        :return: True if the proxy is valid, False otherwise.
        """
        test_url = "https://checkmyip.org/"
        try:
            response = requests.get(test_url, proxies=self.__proxies, timeout=5)
            self.__logger.info(f"Proxy validation response: {response.text.split('<TITLE>')[1].split('</TITLE>')[0]}")
            return response.status_code == 200
        except requests.RequestException as e:
            self.__logger.error(f"Proxy validation error: {e}")
            return False

    def set_proxy(self, host: str, port: int, user: str = None, password: str = None) -> None:
        """
        Sets the proxy settings.

        :param host: Proxy host.
        :param port: Proxy port.
        :param user: (Optional) Username for proxy authentication.
        :param password: (Optional) Password for proxy authentication.
        """
        if user and password:
            proxy = f"http://{user}:{password}@{host}:{port}"
        else:
            proxy = f"http://{host}:{port}"

        self.__proxies = {
            "http": proxy,
            "https": proxy,
        }
        self.update_proxy()

    def get_proxy(self) -> dict:
        """
        Returns the current proxy settings.

        :return: Dictionary containing the current proxy settings.
        """
        return self.__proxies

    def update_proxy(self) -> None:
        """
        Updates the session's proxy settings if the current proxy is valid.
        """
        if self.__validate_proxy():
            self.session.proxies.update(self.__proxies)
        else:
            self.__logger.warning("Proxy validation failed. Proxy not set.")