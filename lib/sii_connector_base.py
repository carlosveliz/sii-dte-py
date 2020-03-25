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
from lib.zeep.sii_plugin import SiiPlugin
from requests import Session


__version__ = '0.1'

class SiiConnectorBase:
	""" Server name """
	_local_wsdl_path_template = 'wsdl/{server-token}/{module}/{module}.wsdl'
	_remote_wsdl_path_template = 'https://{server-token}.sii.cl/DTEWS/{module}.jws?WSDL'
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
	certificate_requiered_modules = ['GetTokenFromSeed']
	GET_SEED_MODULE_ID = 0
	GET_TOKEN_MODULE_ID = 1
	""" SSL activated """
	ssl = 0

	""" SOAP client (Zeep) """
	soap_client = None
	sii_plugin = None

	""" Certificate service """
	_certificate_service = None

	def __init__(self, server='maullin', module=1, mode=1, ssl=0):
		logger = logging.getLogger()
		""" Load certificate """

		self.mode = mode
		self.module = module
		self.ssl = ssl
		self.server = server
		""" Set module and server """
		self.server_url = self.get_wsdl_url(server, module)

		""" Pass SII certificate """
		session = Session()
		session.verify = False
		transport = zeep.Transport(session=session)

		self.sii_plugin = SiiPlugin()

		logger.info("SiiConnectorBase.__init__::Loading WSDL from : " + str(self.server_url))
		self.soap_client = zeep.Client(
			wsdl=self.server_url,
			transport=transport,
			plugins=[self.sii_plugin]
		)

	def generate_certificate(self, pfx_file_path, pfx_password):
		self._certificate_service = CertificateService(pfx_file_path, pfx_password)
		""" Load certificate if needed """
		if self.modules[module] in self.certificate_requiered_modules:
			self._certificate_service.generate_certificate_and_key()
			self.sii_plugin.cert = self._certificate_service.certificate
			self.sii_plugin.key = self._certificate_service.key

	def set_key_and_certificate(self, key, certificate):
		self.sii_plugin.cert = certificate
		self.sii_plugin.key = key

	def get_wsdl_url(self, server, module_code):
		return self._local_wsdl_path_template.replace('{server-token}', server).replace('{module}', self.modules[module_code])

	def unreference_certificate_service(self):
		""" Not sure if it helps, but we ensure that there is no reference
		to current CertificateService to let it be disposed by GC """
		self.certificate_service = None
