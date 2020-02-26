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
	server_url = 'wsdl/{server-token}/{module}/{module}.wsdl'
	mode = 1
	module = 1

	servers = ['palena', 'maullin']
	modes = ['production', 'test']
	modules = [
					'CrSeed', #Authentication, used to generate token for further comunication
					'QueryEstUp' #Query document state
					]

	""" SSL activated """
	ssl = 0

	""" SOAP client (Zeep) """
	soap_client = None

	def __init__(self, server='maullin', module=1, mode=1, ssl=0):
		""" Set module and server """
		self.server_url = self.server_url.replace('{server-token}', server)
		self.server_url = self.server_url.replace('{module}', self.modules[module])
		self.mode = mode
		self.module = module
		self.ssl = ssl
		print("Connecting to : " + str(self.server_url))
		self.soap_client = zeep.Client(wsdl=self.server_url)
