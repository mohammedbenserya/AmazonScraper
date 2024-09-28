import os
import logging
from colorlog import ColoredFormatter
from dotenv import load_dotenv

from datetime import datetime
from pyfiglet import Figlet

from AmazonSmartScraper import __version__

load_dotenv()

# Create logger
logger = logging.getLogger('AmazonSmartScraper')

# Set default log level

default_log_level = logging.INFO
logger.setLevel(default_log_level)


class CustomFileHandler(logging.FileHandler):
    def __init__(self, filename, mode='a', encoding=None, delay=False):
        # Check if the file already exists
        is_file_existing = os.path.isfile(filename)
        super().__init__(filename, mode, encoding, delay)
        # Write the version if the file is newly created
        if not is_file_existing:
            self.print_ascii_banner(f"AmazonSmartScraper py V{__version__}", font="slant")

    def print_ascii_banner(self, text, font: str = "standard"):
        """Prints an ASCII banner using the figlet library.

      Args:
          text: The text to display in the banner.
          font: The desired font for the banner (optional).
      """
        try:
            # Call figlet to generate the banner
            figlet = Figlet(font=font)
            self.stream.write(figlet.renderText(text))
            self.stream.flush()
        except OSError:
            print("figlet library not found. Please install it using 'pip install figlet'.")


if not logger.handlers:
    # Creating a file handler
    # Get the current date
    current_date = datetime.now().date()
    # current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    version = __version__
    # version_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), f'../logs/{version}'))
    log_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logs', version))

    # Ensure the version directory exists
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_file = f'{log_directory}/{current_date}.log'
    # log_file = f'{version_directory}/{current_time}.log'

    file_handler = CustomFileHandler(log_file)
    file_handler.setLevel(default_log_level)

    # Creating a console handler (optional)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(default_log_level)

    plain_formatter = logging.Formatter(
        f'%(asctime)s - %(name)s version {version} - %(filename)s - [%(levelname)s] - %(message)s [in %(pathname)s:%('
        'lineno)d]')
    color_formatter = ColoredFormatter(f'%(log_color)s%(asctime)s - %(name)s version {version} - %(filename)s - [%('
                                       'levelname)s] - %(message)s [in %(pathname)s:%(lineno)d]',
                                       log_colors={
                                           'DEBUG': 'cyan',
                                           'INFO': 'green',
                                           'WARNING': 'yellow',
                                           'ERROR': 'red',
                                           'CRITICAL': 'red,bg_white',
                                       }
                                       )

    # Setting the formatter for the handlers
    file_handler.setFormatter(plain_formatter)
    console_handler.setFormatter(color_formatter)

    # Adding the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
