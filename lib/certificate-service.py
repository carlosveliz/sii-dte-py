
"""

 1- Load certificate
 2- Sign

"""

from lxml import etree
from signxml import XMLSigner, XMLVerifier

class CertificateService:
	def __init__(self):
		print("Not implemented.")

	def set_certificate(self, path):
		""" How to safely store certificate ? """
		print("Not implemented.")

	def sign(self, paylaod, use_loaded_certificate=True, certificate=None):
		""" From signXML sample code """
		""" PFX file usually contain certificate and private key """
		""" Extract from PFX file """
		""" openssl pkcs12 -in [yourfile.pfx] -nocerts -out [keyfile-encrypted.key] """
		""" openssl pkcs12 -in [yourfile.pfx] -clcerts -nokeys -out [certificate.crt] """
		""" openssl rsa -in [keyfile-encrypted.key] -out [keyfile-decrypted.key] """
		cert = open("example.pem").read()
		key = open("example.key").read()
		root = etree.fromstring(paylaod)
		signed_root = XMLSigner().sign(root, key=key, cert=cert)

		return signed_root
