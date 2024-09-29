class FetchPageError(Exception):
    """Custom exception for fetch page errors."""

    def __init__(self, message: str, url: str = '', status_code: int = None):
        super().__init__(message)
        self.url = url
        self.status_code = status_code

    def __str__(self):
        base_message = super().__str__()
        if self.url and self.status_code:
            return f"{base_message} (URL: {self.url}, Status Code: {self.status_code})"
        elif self.url:
            return f"{base_message} (URL: {self.url})"
        elif self.status_code:
            return f"{base_message} (Status Code: {self.status_code})"
        return base_message

class ParsingError(Exception):
    """Custom exception for parsing errors."""

    def __init__(self, message: str, element: str = ''):
        super().__init__(message)
        self.element = element

    def __str__(self):
        base_message = super().__str__()
        if self.element:
            return f"{base_message} (Element: {self.element})"
        return base_message