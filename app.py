from multiprocessing import Process
from time import sleep

from database import *
from views import *
from api import *


def check_expired_urls():
    with app.app_context():
        shortener = Shortener()
        while True:
            shortener.delete_expired_urls()
            sleep(60)


if __name__ == "__main__":
    p_check_expired_urls = Process(target=check_expired_urls)
    p_check_expired_urls.start()
    p_app = Process(target=app.run())
    p_app.start()
