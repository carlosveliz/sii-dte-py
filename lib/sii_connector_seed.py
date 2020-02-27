from lib.sii_connector_base import SiiConnectorBase
from lxml.etree import tostring
import logging
import zeep
import re

class SiiConnectorSeed(SiiConnectorBase):
	""" As discribed in documentation, seed is at least 12 digits """
	REGEX_MATCH_SEED = r"<SEMILLA>(\d{12,})</SEMILLA>"
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
		matches = re.finditer(self.REGEX_MATCH_SEED, response, re.MULTILINE)
		for matchNum, match in enumerate(matches, start=1):
			seed = match.group(1)

		""" Parsing state using RegEX """
		matches = re.finditer(self.REGEX_MATCH_STATE, response, re.MULTILINE)
		for matchNum, match in enumerate(matches, start=1):
			state = match.group(1)

		""" State 00 indicate success """
		if state != "00":
			logger.error("get_seed:: Server respond with invalid state code : " + str(state))

		logger.info("Seed " + str(seed))
		return seed
