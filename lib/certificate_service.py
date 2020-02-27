
"""

 1- Load certificate
 2- Sign

"""

from lxml import etree
import logging
import subprocess

class CertificateService:
	""" Properties """
	certificate = None
	key = None
	_pfx_password = ''
	_pfx_path = ''

	key_path = 'cert/keyfile-encrypted.key'
	cert_path = 'cert/certificate.crt'

	def __init__(self, pfx_file_path, pfx_password=''):
		self._pfx_password = pfx_password
		self._pfx_path = pfx_file_path

	def generate_certificate_and_key(self):
		""" Get logger """
		logger = logging.getLogger()
		logger.info("set_certificate::Loading certificate from " + str(self._pfx_path))
		""" How to safely store certificate ? """
		subprocess.run(["openssl", "pkcs12", "-in", self._pfx_path ,"-passin", "pass:" +self._pfx_password, "-passout","pass:" +self._pfx_password, "-out", self.key_path])
		subprocess.run(["openssl", "pkcs12", "-in", self._pfx_path, "-clcerts", "-nokeys", "-passin", "pass:" +self._pfx_password, "-passout","pass:" +self._pfx_password, "-out", self.cert_path])

	def read_file(self, f_name):
		with open(f_name, "rb") as f:
			return f.read()

	def load_certficate_and_key(self):
		self.certificate = self.read_file(self.cert_path)
		self.key = self.read_file(self.key_path)

	def get_password(self):
		return self._pfx_password
