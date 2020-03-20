"""
This is the file that is invoked to start up a development server.
It gets a copy of the app from your package and runs it.
"""

__version__ = '0.1'

from lib.web import app
from lib.models.sii_token import Token
from lib.sii_connector_auth import SiiConnectorAuth
from lib.certificate_service import CertificateService
from instance.config import FLASK_LISTEN_PORT, FLASK_ENDPOINT, DEBUG_MODE
import logging
import sys

if DEBUG_MODE == True:
	logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s | %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
else:
	logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s | %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logging.info('Application started.')

if len(sys.argv) > 1:
	logging.warning('Diagnose started.')
	diagnose_type = sys.argv[1]
	if diagnose_type == "0":
		logging.warning('Full test.')
		auth = SiiConnectorAuth(pfx_file_path=sys.argv[2], pfx_password=sys.argv[3])
		seed = auth.get_seed()
		print("Seed : " + seed)
		auth = SiiConnectorAuth(server='maullin', \
								module=SiiConnectorAuth.GET_TOKEN_MODULE_ID, \
								pfx_file_path=sys.argv[2], \
								pfx_password=sys.argv[3])
		token = Token(auth.get_token(seed))
		print("Token : " + token)
	if diagnose_type == "1":
		""" Get seed, build token, exit """
		logging.warning('Authentication test.')
		auth = SiiConnectorAuth()
		seed = auth.get_seed()
		print("Seed : " + seed)
		auth = SiiConnectorAuth(server='maullin', \
								module=SiiConnectorAuth.GET_TOKEN_MODULE_ID, \
								pfx_file_path=sys.argv[2], \
								pfx_password=sys.argv[3])
		token = auth.get_token(seed)
		print("Token : " + token)
	elif diagnose_type == "2":
		""" Generate certificate only """
		logging.warning('Certificate generation test.')
		cert = CertificateService(pfx_file_path=sys.argv[2], pfx_password=sys.argv[3])
		cert.generate_certificate_and_key()
else:
	"""
	  Run Flask web app
	"""
	app.run(debug=DEBUG_MODE, host=FLASK_ENDPOINT, port=int(FLASK_LISTEN_PORT))

logging.info('Application stopped.')
