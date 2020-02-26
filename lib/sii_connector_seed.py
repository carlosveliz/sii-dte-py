from lib.sii_connector_base import SiiConnectorBase
from lxml.etree import tostring
import logging
import zeep

class SiiConnectorSeed(SiiConnectorBase):
	""" Default parameters : test server, CrSeed, test, SSL """
	def __init__(self, server='maullin', module=0, mode=1, ssl=1):
		SiiConnectorBase.__init__(self, server, module, mode, ssl)

	def get_seed(self):
		#node = self.soap_client.create_message(self.soap_client.service, 'getSeed')
		#print('Message : ' + str(tostring(node)))
		self.soap_client.transport.session.verify = False
		with self.soap_client.settings(raw_response=True):
			response = self.soap_client.service.getSeed()
			assert response.status_code == 200
			print(str(response.content))
