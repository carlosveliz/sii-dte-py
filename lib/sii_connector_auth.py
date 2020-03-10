from lib.sii_connector_base import SiiConnectorBase
from lxml.etree import tostring
import logging
from requests import Session
from zeep import Client,Transport
from lib.zeep.custom_signature import MemorySignatureOneWay
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

	def read_file(self, f_name):
		with open(f_name, "rb") as f:
			return f.read()

	def get_token(self, seed):
		assert len(seed) >= 12
		""" Get logger """
		logger = logging.getLogger()
		logger.info("get_token:: Getting token")

		seed_template = u'<getToken><item><Semilla>' + seed + '</Semilla></item>' + self.read_file('cert/sign_sii_xml.tmpl').decode('utf-8') + '</getToken>'
		print(str(seed_template))
		seed_message = self.sii_plugin.test_sign_xmlsec(seed_template)
		token = ''

		response = self.soap_client.service.getToken(seed_message)

		""" Parsing response using RegEX """
		match = re.search(self.REGEX_MATCH_TOKEN, token, re.MULTILINE)
		if match:
			token = match.group(1)

		""" Parsing state using RegEX """
		match = re.search(self.REGEX_MATCH_STATE, response, re.MULTILINE)
		if match:
			state = match.group(1)

		""" State 00 indicate success """
		if state != "00":
			logger.error("get_seed:: Server respond with invalid state code : " + str(state))

		return token
