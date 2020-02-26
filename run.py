""" This is the file that is invoked to start up a development server.
It gets a copy of the app from your package and runs it.
 """

__version__ = '0.1'

from lib.web import app
from lib.sii_connector_seed import SiiConnectorSeed
from instance.config import FLASK_LISTEN_PORT, FLASK_ENDPOINT, DEBUG_MODE
import logging

logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s | %(name)s - %(levelname)s - %(message)s')
logging.info('Application started.')

seed = SiiConnectorSeed()
seed.get_seed()


"""
  Run Flask web app
"""
"""app.run(debug=DEBUG_MODE, host=FLASK_ENDPOINT, port=int(FLASK_LISTEN_PORT))"""
