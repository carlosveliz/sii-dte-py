"""
Note :
    Two servers :
        Maullin : Test server
        Palena : Production server

    Base URL :


"""
import zeep
import logging
from lib.certificate_service import CertificateService

__version__ = '0.1'

class SiiConnectorBase:
	""" Server name """
	_wsdl_path_template = 'wsdl/{server-token}/{module}/{module}.wsdl'
	server_url = ''
	mode = 1
	module = 1
	server = ''

	servers = ['palena', 'maullin']
	modes = ['production', 'test']
	modules = [
					'CrSeed', #Authentication, used to generate seed used to request token for further comunication
					'GetTokenFromSeed', #Authentication, get token from seed
					'QueryEstUp' #Query document state
				]

	""" SSL activated """
	ssl = 0

	""" SOAP client (Zeep) """
	soap_client = None

	""" Certificate service """
	certificate_service = None

	def __init__(self, server='maullin', module=1, mode=1, ssl=0, pfx_file_path="", pfx_password=""):
		logger = logging.getLogger()
		""" Load certificate """
		self.certificate_service = CertificateService(pfx_file_path, pfx_password)
		self.mode = mode
		self.module = module
		self.ssl = ssl
		self.server = server
		""" Set module and server """
		self.server_url = self.get_wsdl_url(server, module)

		logger.info("SiiConnectorBase.__init__::Loading WSDL from : " + str(self.server_url))
		self.soap_client = zeep.Client(wsdl=self.server_url)


	def get_wsdl_url(self, server, module_code):
		return self._wsdl_path_template.replace('{server-token}', server).replace('{module}', self.modules[module_code])
