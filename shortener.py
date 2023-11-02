import datetime
from random import choice
from string import ascii_lowercase, digits

from database import *


class Shortener:
    def __init__(self):
        self.chars = ascii_lowercase + digits
        self.chars_len = (
            4
            if len(str(db.session.query(Url).count())) < 4
            else len(str(db.session.query(Url).count()))
        )

    def check_datetime_format(self, datetime_str):
        try:
            datetime.datetime.strptime(datetime_str, "%d-%m-%Y.%H:%M")
            return True
        except:
            return False

    def convert_datetime_format(self, datetime_str):
        datetime_obj = datetime.datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M")
        new_datetime_str = datetime_obj.strftime("%d-%m-%Y.%H:%M")
        return new_datetime_str

    def generate_short_url(self):
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
        # Check if the long URL already exists in the database.
        short_url = Url.query.filter_by(long_url=long_url).first()

        # If the long URL already exists, return the existing short URL.
        # This creates a fatal flaw in the system.
        # If user0 shortened `test.com` and was assigned the short URL `a1c4`,
        # and user1 tried to shorten `test.com`, user1 will also be assigned the same short URL, `a1c4`,
        # but the short URL `a1c4` will still be associated with user0.
        # if short_url is not None:
        #     return short_url.short_url

        # Otherwise, generate a new short URL and store the mapping in the database.
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
        # Look up the short URL in the database and return the corresponding long URL, created date, and expiration date.
        url = Url.query.filter_by(short_url=short_url).first()

        # If the short URL does not exist, return None.
        return url if url is not None else None

    def update_exp_date(self, short_url, expiration_date):
        # Update the expiration date of a URL
        url = Url.query.filter_by(short_url=short_url).first()
        url.expiration_date = expiration_date
        db.session.commit()

    def delete_short_url(self, short_url):
        # Delete the short URL from the database.
        url = Url.query.filter_by(short_url=short_url).first()
        db.session.delete(url)
        db.session.commit()
