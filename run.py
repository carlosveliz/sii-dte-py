"""
This is the file that is invoked to start up a development server.
It gets a copy of the app from your package and runs it.
"""

__version__ = '0.1'
import logging
import sys
import json
from web.router import app
from lib.models.sii_token import Token
from lib.zeep.sii_plugin import SiiPlugin
from lib.models.dte import DTECAF, DTEBuidler, DTECover, DTEPayload
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
		print("Without parameters: launch flask webserver on http://" + str(FLASK_ENDPOINT) + ":" + str(FLASK_LISTEN_PORT) + "")
		print("get_token <pfx_file_path> <pfx_password>")
		print("generate_cert <pfx_file_path> <pfx_password>")
		print("generate_pdf <sii type>")
		print("generate_pdf: Should create test/data/sender.json test/data/sender.json test/data/receiver.json test/data/items.json test/data/specifics.json test/data/caf_test.xml")
		print("generate_xml: <sii type> <pfx_file_path> <pfx_password>")
		print("generate_xml: Should create test/data/sender.json test/data/sender.json test/data/receiver.json test/data/items.json test/data/specifics.json test/data/caf_test.xml")
		print("generate_pdf_from_xml <xml path>")
	if command == "get_token":
		logging.warning('Full test.')
		auth = SiiConnectorAuth(module=SiiConnectorAuth.GET_SEED_MODULE_ID)
		seed = auth.get_seed()
		print("Seed : " + seed)
		auth = SiiConnectorAuth(module=SiiConnectorAuth.GET_TOKEN_MODULE_ID)

		""" Extract key """
		cert = CertificateService(pfx_file_path=sys.argv[2], pfx_password=sys.argv[3])
		cert.generate_certificate_and_key()
		auth.set_key_and_certificate(cert.key, cert.certificate)
		token_string = auth.get_token(seed)
		token = Token(token_string)
		print("Token : " + token.get_token())
	if command == "generate_cert":
		""" Generate certificate only """
		logging.warning('Certificate generation test.')
		cert = CertificateService(pfx_file_path=sys.argv[2], pfx_password=sys.argv[3])
		cert.generate_certificate_and_key()
	if command =="generate_pdf_from_xml":
		pdf = PDFGenerator()
		builder = DTEBuidler()
		_, _, dte_object = builder.from_file(sys.argv[2])
		pdf.generate(dte_object)
	if command =="generate_pdf":
		pdf = PDFGenerator()
		""" Dump test XML """
		type = int(sys.argv[2])

		sender_parameters = {}
		receiver_parameters = {}
		specific_header_parameters = {}
		item_list = {}

		""" Read test files """
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

		""" Bind user information, mocked for this process """
		specific_header_parameters['User'] = {}
		specific_header_parameters['User']['Resolution'] = '80'
		specific_header_parameters['User']['ResolutionDate'] = '2004'
		specific_header_parameters['User']['RUT'] = 'RUT'

		_, pretty_dte, dte_object = builder.build(type, sender_parameters, receiver_parameters, specific_header_parameters, item_list, caf)
		pdf.generate(dte_object)

		""" Add to envelope to be send """
		envelope = {}
		envelope[1] = dte_object

		""" Generate cover (Caratula) """
		cover = DTECover(dtes=envelope, resolution={'Date': '2014-08-22', 'Number': '80'}, user={'RUT':'25656563-3'})
		""" Generate payload to be uploaded (without signature, only tagged)"""
		payload = DTEPayload(dtes=envelope, cover=cover, user={})
		""" Write ready-to-upload XML  (without signature) """
		myXML = open('temp/DTE_ENV' + str(type) + '.xml', "w")
		myXML.write(payload.dump())
	if command =="generate_xml":
		pdf = PDFGenerator()
		""" Dump test XML """
		type = int(sys.argv[2])

		sender_parameters = {}
		receiver_parameters = {}
		specific_header_parameters = {}
		item_list = {}

		""" Read test files """
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

		""" Bind user information, mocked for this process """
		specific_header_parameters['User'] = {}
		specific_header_parameters['User']['Resolution'] = '80'
		specific_header_parameters['User']['ResolutionDate'] = '2004'
		specific_header_parameters['User']['RUT'] = 'RUT'

		_, pretty_dte, dte_object = builder.build(type, sender_parameters, receiver_parameters, specific_header_parameters, item_list, caf)

		""" Add to envelope to be send """
		envelope = {}
		envelope[1] = dte_object

		""" Generate cover (Caratula) """
		cover = DTECover(dtes=envelope, resolution={'Date': '2014-08-22', 'Number': '80'}, user={'RUT':'25656563-3'})
		""" Generate payload to be uploaded (without signature, only tagged)"""
		payload = DTEPayload(dtes=envelope, cover=cover, user={})
		siiSignature = SiiPlugin()
		""" Load key """
		cert = CertificateService(pfx_file_path=sys.argv[3], pfx_password=sys.argv[4])
		cert.generate_certificate_and_key()
		siiSignature.key = cert.key
		siiSignature.cert = cert.certificate

		""" Remove declaration """
		declare = '<?xml version="1.0" encoding="ISO-8859-1"?>'
		payload = payload.dump().replace(declare, '')
		ready_to_upload = siiSignature.sign_tagged_message(payload)
		""" Add declaration back """
		ready_to_upload = declare + '\n\r' + ready_to_upload
		""" Write ready-to-upload XML  (without signature) """
		myXML = open('temp/DTE_ENV' + str(type) + '.xml', "w")
		myXML.write(ready_to_upload)
		print("Done.")
else:
	"""
	  Run Flask web app
	"""
	print("Type run.py help to show all available commands")
	logging.info('Web server started on ' + str(FLASK_ENDPOINT) + ':' + str(FLASK_LISTEN_PORT))
	app.run(debug=DEBUG_MODE, host=FLASK_ENDPOINT, port=int(FLASK_LISTEN_PORT))

logging.info('Application stopped.')
