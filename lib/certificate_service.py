
"""

 1- Load certificate
 2- Sign

"""

from lxml import etree
import logging
import subprocess

class CertificateService:
	""" Properties """
	_certificate = ''
	_key = ''
	_pfx_password = ''
	_pfx_path = ''

	def __init__(self, pfx_file_path, pfx_password=''):
		self._pfx_password = pfx_password
		self._pfx_path = pfx_file_path

	def generate_certificate_and_key(self):
		""" Get logger """
		logger = logging.getLogger()
		logger.info("set_certificate::Loading certificate from " + str(self._pfx_path))
		""" How to safely store certificate ? """
		subprocess.run(["openssl", "pkcs12", "-in", self._pfx_path, "-nocerts" ,"-passin", "pass:" +self._pfx_password, "-passout","pass:" +self._pfx_password, "-out", "cert/keyfile-encrypted.key"])
		subprocess.run(["openssl", "pkcs12", "-in", self._pfx_path, "-clcerts", "-nokeys", "-passin", "pass:" +self._pfx_password, "-passout","pass:" +self._pfx_password, "-out", "cert/certificate.crt"])
