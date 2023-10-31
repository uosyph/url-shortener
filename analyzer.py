from flask import request
from ua_parser import user_agent_parser
from ip2geotools.databases.noncommercial import DbIpCity
from geopy.distance import distance
import datetime

from database import *


class Analyzer:
    def __init__(self):
        self.short_url = ""
        self.user_agent = ""
        self.response_time = ""
        self.user_details = user_agent_parser.Parse(self.user_agent)

    def get_click_time(self):
        return datetime.datetime.now().strftime("%d-%m-%Y.%H:%M:%S")

    def get_platform(self):
        return self.user_details["os"]["family"]

    def get_browser(self):
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
        if request.environ.get("HTTP_X_FORWARDED_FOR") is None:
            return request.environ["REMOTE_ADDR"]
        else:
            # if behind a proxy
            return request.environ["HTTP_X_FORWARDED_FOR"]

    def get_location(self):
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
        client_ip = self.get_ip()
        server_ip = request.remote_addr
        client_details = DbIpCity.get(client_ip)
        server_details = DbIpCity.get(server_ip)
        return distance(
            (client_details.latitude, client_details.longitude),
            (server_details.latitude, server_details.longitude),
        ).km

    def track(self):
        client_location = self.get_location()

        new_stat = Stat(
            short_url=self.short_url,
            click_time=self.get_click_time(),
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
        urls = db.session.query(Stat).where(Stat.short_url == self.short_url)
        return urls.count()

    def delete(self):
        urls = db.session.query(Stat).where(Stat.short_url == self.short_url)
        for url in urls:
            db.session.delete(url)
            db.session.commit()
