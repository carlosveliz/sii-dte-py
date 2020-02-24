"""
Note :
    Two servers :
        Maullin : Test server
        Palena : Production server

    Base URL :


"""

__version__ = '0.1'

class SiiConnector:
	""" Server name """
	self.server_url = 'https://{server-token}.sii.cl/DTEWS/{servicio}.jws?WSDL'
	self.mode = 1

	self.servers = {'palena', 'maullin'}
	self.modes = {'production', 'test'}

	""" SSL activated """
	self.ssl = 0

	def __init__(self, server='maullin', mode=1, ssl=0):
		self.server_url = self.server_url.replace('{server-token}', server)
		self.mode = mode
		self.ssl = ssl
