from time import sleep

from database import *
from views import *
from api import *

app.run()

while True:
    Shortener().delete_expired_urls()
    sleep(60)
