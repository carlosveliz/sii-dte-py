#
__version__ = '0.1'
import datetime

from flask import Flask

app = Flask(__name__, instance_relative_config=True)

""" Basic key, ensures that is changes everytime with start the application """
#epoch = datetime.datetime.utcfromtimestamp(0)
#app.secret_key = str(epoch)
app.secret_key = "MyOwnSuperSecretKeyYouCantCrack"
print(" * Application secret key : " + app.secret_key)

from lib.web import router
