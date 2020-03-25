"""
This is the file that is invoked to start up a development server.
It gets a copy of the app from your package and runs it.
"""

__version__ = '0.1'
import logging
import sys
import json
from lib.web import app
from lib.models.sii_token import Token
from lib.models.dte import DTECAF, DTEBuidler
from lib.sii_connector_auth import SiiConnectorAuth
from lib.certificate_service import CertificateService
from lib.pdf_generator import PDFGenerator
from instance.config import FLASK_LISTEN_PORT, FLASK_ENDPOINT, DEBUG_MODE


if DEBUG_MODE == True:
	logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s | %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
else:
	logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s | %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logging.info('Application started.')

if len(sys.argv) > 1:
	command = sys.argv[1]
	if command == "help":
		print("get_token <pfx_file_path> <pfx_password>")
		print("generate_cert <pfx_file_path> <pfx_password>")
		print("generate_pdf <sii type>")
	if command == "get_token":
		logging.warning('Full test.')
		auth = SiiConnectorAuth(pfx_file_path=sys.argv[2], pfx_password=sys.argv[3])
		seed = auth.get_seed()
		print("Seed : " + seed)
		auth = SiiConnectorAuth(server='maullin', \
								module=SiiConnectorAuth.GET_TOKEN_MODULE_ID, \
								pfx_file_path=sys.argv[2], \
								pfx_password=sys.argv[3])
		token_string = auth.get_token(seed)
		token = Token(token_string)
		print("Token : " + token.get_token())
	if command == "generate_cert":
		""" Generate certificate only """
		logging.warning('Certificate generation test.')
		cert = CertificateService(pfx_file_path=sys.argv[2], pfx_password=sys.argv[3])
		cert.generate_certificate_and_key()
	if command =="generate_pdf":
			pdf = PDFGenerator()
			""" Dump test XML """
			type = int(sys.argv[2])

			sender_parameters = {}
			receiver_parameters = {}
			specific_header_parameters = {}
			item_list = {}

			with open('test/data/sender.json') as json_file:
				sender_parameters = json.load(json_file)
			with open('test/data/receiver.json') as json_file:
				receiver_parameters = json.load(json_file)
			with open('test/data/items.json') as json_file:
				item_list = json.load(json_file)
			with open('test/data/specifics.json') as json_file:
				specific_header_parameters = json.load(json_file)

			caf = DTECAF(parameters={}, signature='', private_key='')
			caf.load_from_XML('test/data/caf_test.xml')

			builder = DTEBuidler()

			_, pretty_dte, dte_object = builder.build(type, sender_parameters, receiver_parameters, specific_header_parameters, item_list, caf)
			pdf.generate(dte_object)

			myXML = open('temp/DTE_' + str(type) + '.xml', "w")
			myXML.write(pretty_dte)
else:
	"""
	  Run Flask web app
	"""
	app.run(debug=DEBUG_MODE, host=FLASK_ENDPOINT, port=int(FLASK_LISTEN_PORT))

logging.info('Application stopped.')
