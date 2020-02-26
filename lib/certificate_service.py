
"""

 1- Load certificate
 2- Sign

"""

from lxml import etree
from signxml import XMLSigner, XMLVerifier

class CertificateService:
	""" Properties """
	self._certificate = ''
	self._key = ''

	def __init__(self):
		print("Not implemented.")

	def set_certificate(self, path):
		""" How to safely store certificate ? """
		print("Not implemented.")

	def sign(self, paylaod, use_loaded_certificate=True, pfx_file_path=None, passphrase=''):
		""" From signXML sample code """
		""" PFX file usually contain certificate and private key """
		""" Extract from PFX file """
		""" openssl pkcs12 -in [yourfile.pfx] -nocerts -out [keyfile-encrypted.key] """
		""" openssl pkcs12 -in [yourfile.pfx] -clcerts -nokeys -out [certificate.crt] """
		""" Passphrase needed to decrypt key """

		system.exec("openssl pkcs12 -in " + pfx_file_path + " -nocerts -out keyfile-encrypted.key")
		system.exec("openssl pkcs12 -in " + pfx_file_path + " -clcerts -nokeys -out certificate.crt")

		if use_loaded_certificate == False:
			cert = open("certificate.crt").read()
			key = open("keyfile-encrypted.key").read()
			self._certificate = cert
			self._key = key

		root = etree.fromstring(paylaod)
		signed_root = XMLSigner().sign(root, key=self._key, cert=self._certificate, passphrase=passphrase)

		return signed_root
