"""
URL Shortener Web Application Main Script

This script serves as the entry point for the URL shortener web application.
Providing functionality for both the web application and the API.

Author: Yousef Saeed
"""

from multiprocessing import Process
from time import sleep

from database import *
from views import *
from api import *


def check_expired_urls():
    """
    Function to periodically check and delete expired URLs.

    This function runs in a loop and periodically checks for expired URLs using the Shortener class.
    If an expired URL is found, it will be deleted. It sleeps for 60 seconds between checks.

    This function is intended to be run in a separate process.
    """

    with app.app_context():
        shortener = Shortener()
        while True:
            shortener.delete_expired_urls()
            sleep(60)


if __name__ == "__main__":
    # Create a separate process to run the URL expiration checker
    p_check_expired_urls = Process(target=check_expired_urls)
    p_check_expired_urls.start()

    # Create a separate process to run the Flask application
    p_app = Process(target=app.run())
    p_app.start()
