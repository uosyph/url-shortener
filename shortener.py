"""
URL Shortener Module

This module provides a URL shortening service that allows users to generate short URLs for long web addresses.
It includes functionality for creating, managing, and resolving short URLs.
The short URLs can have an optional expiration date and can be associated with a user ID.

The module uses a database to store URL mappings, and it can also delete expired short URLs and associated analytics data.

Classes:
    - Shortener: The main class for URL shortening, including methods for generating, managing, and resolving short URLs.

Author: Yousef Saeed
"""

import datetime
from random import choice
from string import ascii_lowercase, digits

from database import *


class Shortener:
    """
    Shortener is a class for generating, managing, and resolving short URLs.

    Attributes:
        chars (str): A string containing lowercase letters and digits for generating short URLs.
        chars_len (int): The length of the characters used in short URLs, determined based on the number of URLs in the database.

    Methods:
        - check_datetime_format(datetime_str)
        - convert_datetime_format(datetime_str)
        - generate_short_url()
        - shorten_url(long_url, expiration_date=None, is_permanent=False, user_id=None)
        - resolve_short_url(short_url)
        - update_exp_date(short_url, expiration_date)
        - delete_short_url(short_url)
        - delete_expired_urls()
    """

    def __init__(self):
        """
        Initialize Shortener with character set and character length.
        """

        self.chars = ascii_lowercase + digits
        self.chars_len = (
            4
            if len(str(db.session.query(Url).count())) < 4
            else len(str(db.session.query(Url).count()))
        )

    def check_datetime_format(self, datetime_str):
        """
        Check if a datetime string is in the format "%d-%m-%Y.%H:%M".

        Args:
            datetime_str (str): The datetime string to check.

        Returns:
            bool: True if the datetime string is in the expected format, False otherwise.
        """

        try:
            datetime.datetime.strptime(datetime_str, "%d-%m-%Y.%H:%M")
            return True
        except:
            return False

    def convert_datetime_format(self, datetime_str):
        """
        Convert a datetime string from "%Y-%m-%dT%H:%M" to "%d-%m-%Y.%H:%M" format.

        Args:
            datetime_str (str): The datetime string in the original format.

        Returns:
            str: The datetime string in the new format.
        """

        datetime_obj = datetime.datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M")
        new_datetime_str = datetime_obj.strftime("%d-%m-%Y.%H:%M")
        return new_datetime_str

    def generate_short_url(self):
        """
        Generate a random short URL.

        Returns:
            str: A randomly generated short URL.
        """

        # Generate a random string of 6 characters.
        short_url = "".join([choice(self.chars) for _ in range(self.chars_len)])

        # Check if the short URL already exists in the database.
        url = Url.query.filter_by(short_url=short_url).first()

        # If the short URL already exists, generate a new one.
        while url is not None:
            short_url = "".join([choice(self.chars) for _ in range(self.chars_len)])
            url = Url.query.filter_by(short_url=short_url).first()

        return short_url

    def shorten_url(
        self, long_url, expiration_date=None, is_permanent=False, user_id=None
    ):
        """
        Shorten a long URL and store it in the database.

        Args:
            long_url (str): The long URL to be shortened.
            expiration_date (str, optional): The expiration date of the short URL.
            is_permanent (bool, optional): Indicates whether the short URL is permanent.
            user_id (int, optional): The user ID associated with the short URL.

        Returns:
            str: The generated short URL.
        """

        # Generate a new short URL and store the mapping in the database.
        short_url = Url.query.filter_by(long_url=long_url).first()
        short_url = self.generate_short_url()
        creation_date = datetime.datetime.now().strftime("%d-%m-%Y.%H:%M:%S")
        if expiration_date is None and is_permanent == False:
            expiration_date = (
                datetime.datetime.now() + datetime.timedelta(days=7)
            ).strftime("%d-%m-%Y.%H:%M")
        new_url = Url(
            short_url=short_url,
            long_url=long_url,
            creation_date=creation_date,
            expiration_date=expiration_date,
            is_permanent=is_permanent,
            user_id=user_id,
        )
        db.session.add(new_url)
        db.session.commit()

        return short_url

    def resolve_short_url(self, short_url):
        """
        Resolve a short URL and return its details.

        Args:
            short_url (str): The short URL to be resolved.

        Returns:
            Url: The URL object with the corresponding details, or None if the short URL does not exist.
        """

        url = Url.query.filter_by(short_url=short_url).first()

        return url if url is not None else None

    def update_exp_date(self, short_url, expiration_date):
        """
        Update the expiration date of a short URL in the database.

        Args:
            short_url (str): The short URL to be updated.
            expiration_date (str): The new expiration date in "%d-%m-%Y.%H:%M" format.

        Returns:
            None
        """

        url = Url.query.filter_by(short_url=short_url).first()
        url.expiration_date = expiration_date
        db.session.commit()

    def delete_short_url(self, short_url):
        """
        Delete a short URL from the database.

        Args:
            short_url (str): The short URL to be deleted.

        Returns:
            None
        """

        url = Url.query.filter_by(short_url=short_url).first()
        db.session.delete(url)
        db.session.commit()

    def delete_expired_urls(self):
        """
        Delete expired short URLs from the database and associated analytics data.

        Returns:
            None
        """

        current_time = datetime.datetime.now().strftime("%d-%m-%Y.%H:%M")
        expired_urls = db.session.query(Url).where(Url.expiration_date <= current_time)
        if expired_urls.count() > 0:
            from analyzer import Analyzer

            analyzer = Analyzer()
            for url in expired_urls:
                analyzer.short_url = url.short_url
                analyzer.delete()
                db.session.delete(url)
                db.session.commit()
