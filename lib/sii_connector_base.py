"""
Note :
    Two servers :
        Maullin : Test server
        Palena : Production server

    Base URL :


"""
import zeep

__version__ = '0.1'

class SiiConnectorBase:
	""" Server name """
	self.server_url = 'https://{server-token}.sii.cl/DTEWS/{module}.jws?WSDL'
	self.mode = 1
	self.module = 1

	self.servers = {'palena', 'maullin'}
	self.modes = {'production', 'test'}
	self.modules = {
					'CrSeed', #Authentication, used to generate token for further comunication
					'QueryEstUp' #Query document state
					}

	""" SSL activated """
	self.ssl = 0

	""" SOAP client (Zeep) """
	self.soap_client = None

	def __init__(self, server='maullin', module=1, mode=1, ssl=0):
		""" Set module and server """
		self.server_url = self.server_url.replace('{server-token}', server)
		self.server_url = self.server_url.replace('{module}', self.modules[module])
		self.mode = mode
		self.module = module
		self.ssl = ssl

		self.soap_client = zeep.Client(wsdl=self.server_url)
