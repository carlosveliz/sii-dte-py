from lib.sii_connector_base import SiiConnectorBase
from lxml.etree import tostring
import logging
from requests import Session
from zeep import Client,Transport
from lib.zeep.sii_plugin import SiiPlugin
from zeep.exceptions import SignatureVerificationFailed
import re

class SiiConnectorAuth(SiiConnectorBase):
	""" As discribed in documentation, seed is at least 12 digits """
	REGEX_MATCH_SEED = r"<SEMILLA>(\d{12,})</SEMILLA>"
	REGEX_MATCH_TOKEN = r"<TOKEN>(\w{8,})</TOKEN>"
	""" State seems to be at least 3 digits """
	REGEX_MATCH_STATE = r"<ESTADO>(\d{2,})</ESTADO>"

	""" Default parameters : test server, CrSeed, test, SSL """
	def __init__(self, server='maullin', module=0, mode=1, ssl=1):
		SiiConnectorBase.__init__(self, server, module, mode, ssl)

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

	def read_file(self, f_name):
		with open(f_name, "rb") as f:
			return f.read()

	def get_token(self, seed):
		assert len(seed) >= 12
		""" Get logger """
		logger = logging.getLogger()
		logger.debug("get_token:: Getting token")
		token = ''
		token_message = self.build_token_message(seed)

		response = self.soap_client.service.getToken(token_message)

		""" Parsing response using RegEX """
		match = re.search(self.REGEX_MATCH_TOKEN, response, re.MULTILINE)
		if match:
			token = match.group(1)

		""" Parsing state using RegEX """
		match = re.search(self.REGEX_MATCH_STATE, response, re.MULTILINE)
		if match:
			state = match.group(1)

		""" State 00 indicate success """
		if state == "10" or state == "11":
			logger.error("get_token:: Server respond with invalid state code : " + str(state) + " certificate might not be registered in SII.")
		if state != "00":
			logger.error("get_token:: Server respond with invalid state code : " + str(state))

		""" Unload certificate """
		self.unreference_certificate_service()

		return token

	def build_token_message(self, seed):
		""" Get logger """
		logger = logging.getLogger()
		""" Build token template (Message + Signature) """
		token_template = u'<getToken><item><Semilla>' + seed + '</Semilla></item>' + self.read_file('cert/sign_sii_xml.tmpl').decode('utf-8') + '</getToken>'

		token_message = self.sii_plugin.sign(token_template)
		""" Add XML standard header """
		token_message = '<?xml version="1.0" encoding="UTF-8"?> ' + token_message
		logger.debug("build_token_message:: Message :")
		logger.debug(str(token_message))
		return token_message
