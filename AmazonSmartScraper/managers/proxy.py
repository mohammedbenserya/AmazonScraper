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

    def __validate_proxy(self):
        """
        Validates the current proxy settings by checking the IP address.

        This method sends a request to 'https://checkmyip.com' using the current proxy settings
        and compares the IP address before and after setting the proxy. If the IP addresses
        are different, the proxy is considered valid.

        :return: True if the proxy is valid, False otherwise.
        """
        try:
            response = requests.get("https://api.ipify.org?format=text", proxies=self.__proxies)
            current_ip = response.text
            if response.status_code == 200 :
                response =requests.get("https://api.ipify.org?format=text")
                if response.status_code == 200:
                    original_ip = response.text
                    if current_ip != original_ip:
                        self.__logger.info(f"Current IP: {current_ip}, Current IP: {original_ip}")
                        return True
        except Exception as e:
            self.__logger.error(f"Proxy validation failed: {e}")
        self.__logger.error("Proxy validation failed")
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
        if self.session is None:
            self.__logger.error("Session is not initialized.")
            return
        if self.__validate_proxy():
            self.session.proxies.update(self.__proxies)
        else:
            self.__logger.warning("Proxy validation failed. Proxy not set.")