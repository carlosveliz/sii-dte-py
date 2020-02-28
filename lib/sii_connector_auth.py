from lib.sii_connector_base import SiiConnectorBase
from lxml.etree import tostring
import logging
from requests import Session
from zeep import Client,Transport
from lib.zeep.custom_signature import MemorySignatureOneWay
from zeep.exceptions import SignatureVerificationFailed
import re

class SiiConnectorAuth(SiiConnectorBase):
	""" As discribed in documentation, seed is at least 12 digits """
	REGEX_MATCH_SEED = r"<SEMILLA>(\d{12,})</SEMILLA>"
	""" State seems to be at least 3 digits """
	REGEX_MATCH_STATE = r"<ESTADO>(\d{2,})</ESTADO>"

	""" Default parameters : test server, CrSeed, test, SSL """
	def __init__(self, server='maullin', module=0, mode=1, ssl=1, pfx_file_path="", pfx_password=""):
		SiiConnectorBase.__init__(self, server, module, mode, ssl, pfx_file_path, pfx_password)

	"""
		Retrieve "SEMILLA" (seed) used for authentication
	"""
	def get_seed(self):
		""" Get logger """
		logger = logging.getLogger()
		""" Calling getSeed SOAP method """
		response = self.soap_client.service.getSeed()
		""" Parsing response using RegEX """
		match = re.search(self.REGEX_MATCH_SEED, response, re.MULTILINE)
		if match:
			seed = match.group(1)

		""" Parsing state using RegEX """
		match = re.search(self.REGEX_MATCH_STATE, response, re.MULTILINE)
		if match:
			state = match.group(1)

		""" State 00 indicate success """
		if state != "00":
			logger.error("get_seed:: Server respond with invalid state code : " + str(state))

		logger.info("Seed " + str(seed))
		return seed

	def get_token(self, seed):
		assert len(seed) >= 12
		""" Get logger """
		logger = logging.getLogger()
		logger.info("get_token:: Getting token")
		""" Must instanciate another client with Signature enabled """
		token_service_wsdl = self.get_wsdl_url(self.server, 1)
		logger.info("get_token:: WSDL : "+ str(token_service_wsdl))
		self.certificate_service.load_certficate_and_key()

		""" Pass SII certificate """
		session = Session()
		session.verify = False
		transport = Transport(session=session)

		self.soap_client = Client(
			wsdl=token_service_wsdl,
			wsse=MemorySignatureOneWay(
				self.certificate_service.key, self.certificate_service.certificate,
				self.certificate_service.get_password()
			),
			transport=transport
		)
		try:
			token = self.soap_client.service.getToken(seed)
		except SignatureVerificationFailed:
			logger.info("get_token:: SII doesn't sign response.")
			pass

		return token
