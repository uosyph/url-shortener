"""
URL Analyzer Module

This module provides analytics functionality for tracking user interactions with short URLs.
It collects information about user agents, response times, IP addresses, and geolocation data.
It can generate statistics such as entry times, platform usage, browser usage, and location information for a given short URL.

Classes:
    - Analyzer: The main class for tracking and analyzing user interactions with short URLs.

Author: Yousef Saeed
"""

from flask import request
from sqlalchemy import func, Float
from ua_parser import user_agent_parser
from ip2geotools.databases.noncommercial import DbIpCity
from geopy.distance import distance
from statistics import multimode
import datetime

from database import *


class Analyzer:
    """
    Analyzer is a class for tracking and analyzing user interactions with short URLs.

    Attributes:
        - short_url (str): The short URL being analyzed.
        - user_agent (str): The user agent string from the client's browser.
        - response_time (str): The response time of the server.

    Methods:
        - get_entry_time()
        - get_platform()
        - get_browser()
        - get_ip()
        - get_location()
        - get_distance()
        - track()
        - total_entries()
        - total_unique_entries()
        - most_frequent_times()
        - analyze(short_url=None)
        - delete()
    """

    def __init__(self):
        """
        Initialize Analyzer with default attributes and parse user agent details.
        """

        self.short_url = ""
        self.user_agent = ""
        self.response_time = ""
        self.user_details = user_agent_parser.Parse(self.user_agent)

    def get_entry_time(self):
        """
        Get the current entry time in the format "%d-%m-%Y.%H:%M:%S".

        Returns:
            str: The current entry time.
        """

        return datetime.datetime.now().strftime("%d-%m-%Y.%H:%M:%S")

    def get_platform(self):
        """
        Get the platform (OS) of the client from the user agent.

        Returns:
            str: The platform (OS) of the client.
        """

        return self.user_details["os"]["family"]

    def get_browser(self):
        """
        Get the browser and version from the user agent.

        Returns:
            str: The browser and its version.
        """

        browser = self.user_details["user_agent"]["family"]
        browser_version = ".".join(
            [
                self.user_details["user_agent"][key]
                for key in ("major", "minor", "patch")
                if self.user_details["user_agent"][key] is not None
            ]
        )
        return f"{browser}-{browser_version}"

    def get_ip(self):
        """
        Get the client's IP address, considering the possibility of being behind a proxy.

        Returns:
            str: The client's IP address.
        """

        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        return client_ip

    def get_location(self):
        """
        Get geolocation details (city, region, country, latitude, longitude) of the client based on their IP address.

        Returns:
            dict: Geolocation details of the client.
        """

        client_ip = self.get_ip()
        client_details = DbIpCity.get(client_ip)
        return {
            "city": client_details.city,
            "region": client_details.region,
            "country": client_details.country,
            "latitude": client_details.latitude,
            "longitude": client_details.longitude,
        }

    def get_distance(self):
        """
        Calculate the distance in kilometers between the client and the server based on their IP addresses' geolocation.

        Returns:
            float: The distance between the client and the server.
        """

        client_ip = self.get_ip()
        server_ip = request.remote_addr
        client_details = DbIpCity.get(client_ip)
        server_details = DbIpCity.get(server_ip)
        return distance(
            (client_details.latitude, client_details.longitude),
            (server_details.latitude, server_details.longitude),
        ).km

    def track(self):
        """
        Track user interactions and store the details in the database as a Stat record.

        Returns:
            None
        """

        client_location = self.get_location()

        new_stat = Stat(
            short_url=self.short_url,
            entry_time=self.get_entry_time(),
            response_time=self.response_time,
            platform=self.get_platform(),
            browser=self.get_browser(),
            ip=self.get_ip(),
            city=client_location["city"],
            region=client_location["region"],
            country=client_location["country"],
            latitude=client_location["latitude"],
            longitude=client_location["longitude"],
            distance=f"{self.get_distance():.10f}",
        )
        db.session.add(new_stat)
        db.session.commit()

    def total_entries(self):
        """
        Calculate the total number of entries for the current short URL.

        Returns:
            int: The total number of entries.
        """

        urls = db.session.query(Stat).where(Stat.short_url == self.short_url)
        return urls.count()

    def total_unique_entries(self):
        """
        Calculate the total number of unique entries (unique IPs) for the current short URL.

        Returns:
            int: The total number of unique entries.
        """

        urls = (
            db.session.query(Stat)
            .where(Stat.short_url == self.short_url)
            .group_by(Stat.ip)
        )
        return urls.count()

    def most_frequent_times(self):
        """
        Determine the most frequent entry times of the day, month, and year for the current short URL.

        Returns:
            tuple: A tuple containing the most frequent entry times of the day, month, and year.
        """

        urls = db.session.query(Stat).where(Stat.short_url == self.short_url)
        hours_list = []
        days_list = []
        months_list = []
        for url in urls:
            time = datetime.datetime.strptime(
                url.entry_time, "%d-%m-%Y.%H:%M:%S"
            ).strftime("%H")
            day = datetime.datetime.strptime(
                url.entry_time, "%d-%m-%Y.%H:%M:%S"
            ).strftime("%d")
            month = datetime.datetime.strptime(
                url.entry_time, "%d-%m-%Y.%H:%M:%S"
            ).strftime("%m")
            hours_list.append(time)
            days_list.append(day)
            months_list.append(month)
        return multimode(hours_list), multimode(days_list), multimode(months_list)

    def analyze(self, short_url=None):
        """
        Analyze user interactions and generate statistics for a given short URL.

        Args:
            short_url (str, optional): The short URL to analyze. If not provided, uses the stored short URL.

        Returns:
            dict: A dictionary containing various statistics and details of user interactions.
        """

        if short_url is not None:
            self.short_url = short_url

        entries = (
            db.session.query(Stat.entry_time)
            .where(Stat.short_url == self.short_url)
            .all()
        )
        entries = [{"entry": entry[0]} for entry in entries]

        total_entries_count = self.total_entries()
        total_unique_entries_count = self.total_unique_entries()

        times = self.most_frequent_times()
        most_frequent_entry_time_of_day = times[0]
        most_frequent_entry_time_of_month = times[1]
        most_frequent_entry_time_of_year = times[2]

        average_response_time = (
            db.session.query(func.avg(func.cast(Stat.response_time, Float)))
            .where(Stat.short_url == self.short_url)
            .scalar()
        )

        top_platforms = (
            db.session.query(Stat.platform, func.count(Stat.platform))
            .where(Stat.short_url == self.short_url)
            .group_by(Stat.platform)
            .order_by(func.count(Stat.platform).desc())
            .limit(3)
            .all()
        )
        top_platforms = [
            {"platform": platform[0], "count": platform[1]}
            for platform in top_platforms
        ]

        top_browsers = (
            db.session.query(Stat.browser, func.count(Stat.browser))
            .where(Stat.short_url == self.short_url)
            .group_by(Stat.browser)
            .order_by(func.count(Stat.browser).desc())
            .limit(3)
            .all()
        )
        top_browsers = [
            {"browser": browser[0], "count": browser[1]} for browser in top_browsers
        ]

        top_countries = (
            db.session.query(Stat.country, func.count(Stat.country))
            .where(Stat.short_url == self.short_url)
            .group_by(Stat.country)
            .order_by(func.count(Stat.country).desc())
            .limit(10)
            .all()
        )
        top_countries = [
            {"country": country[0], "count": country[1]} for country in top_countries
        ]

        top_regions = (
            db.session.query(Stat.region, func.count(Stat.region))
            .where(Stat.short_url == self.short_url)
            .group_by(Stat.region)
            .order_by(func.count(Stat.region).desc())
            .limit(10)
            .all()
        )
        top_regions = [
            {"region": region[0], "count": region[1]} for region in top_regions
        ]

        top_cities = (
            db.session.query(Stat.city, func.count(Stat.city))
            .where(Stat.short_url == self.short_url)
            .group_by(Stat.city)
            .order_by(func.count(Stat.city).desc())
            .limit(10)
            .all()
        )
        top_cities = [{"city": city[0], "count": city[1]} for city in top_cities]

        average_distance = (
            db.session.query(func.avg(func.cast(Stat.distance, Float)))
            .where(Stat.short_url == self.short_url)
            .scalar()
        )

        return {
            "entries": entries,
            "total_entries_count": total_entries_count,
            "total_unique_entries_count": total_unique_entries_count,
            "most_frequent_entry_time_of_day": most_frequent_entry_time_of_day,
            "most_frequent_entry_time_of_month": most_frequent_entry_time_of_month,
            "most_frequent_entry_time_of_year": most_frequent_entry_time_of_year,
            "average_response_time": average_response_time,
            "top_platforms": top_platforms,
            "top_browsers": top_browsers,
            "top_countries": top_countries,
            "top_regions": top_regions,
            "top_cities": top_cities,
            "average_distance": average_distance,
        }

    def delete(self):
        """
        Delete all records associated with the current short URL from the database.

        Returns:
            None
        """

        urls = db.session.query(Stat).where(Stat.short_url == self.short_url)
        for url in urls:
            db.session.delete(url)
            db.session.commit()
