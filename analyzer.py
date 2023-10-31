from flask import request
from ua_parser import user_agent_parser
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

    def track(self):
        new_stat = Stat(
            short_url=self.short_url,
            click_time=self.get_click_time(),
            response_time=self.response_time,
            platform=self.get_platform(),
            browser=self.get_browser(),
            ip=self.get_ip(),
            location="None",
        )
        db.session.add(new_stat)
        db.session.commit()

    def delete(self):
        urls = db.session.query(Stat).where(Stat.short_url == self.short_url)
        for url in urls:
            db.session.delete(url)
            db.session.commit()
