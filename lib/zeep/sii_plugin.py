from zeep import Plugin
from lxml import etree
import xmlsec
import base64
import logging

class SiiPlugin(Plugin):
	key = ''
	cert = ''
	SIGNATURE_TAG = '[[SIGNATURE]]'

	def ingress(self, envelope, http_headers, operation):
		""" Hook on received messages """
		return envelope, http_headers

	def egress(self, envelope, http_headers, operation, binding_options):
		logger = logging.getLogger()
		""" Hook on sent messages to override behavior if needed """
		if("getToken" == operation.name):
			print(str(operation.name))
		elif("getSemilla" in operation.name):
			print(str(operation.name))
		else:
			print(str(operation.name))

		return envelope, http_headers

	def sign_with_algorithm(self, message, Algorithm='RSAxSHA1'):
		""" SII specified RSA over SHA1 """
		ctx = xmlsec.SignatureContext()
		ctx.key = xmlsec.Key.from_memory(key, format=xmlsec.constants.KeyDataFormatPem)
		""" Flatten data """
		data = data.replace('\n', ' ').replace('\r', '').replace('\t', '').replace('> ', '>').replace(' <', '<')
		data = bytes(data, 'ISO-8859-1')
		sign = ctx.sign_binary(data, xmlsec.constants.TransformRsaSha1)
		""" To base 64 and back to ISO-8859-1"""
		base64_encoded_data = base64.b64encode(sign)
		return base64_encoded_data.decode('ISO-8859-1')

	def read_file(self, f_name):
		with open(f_name, "rb") as f:
			return f.read()

	def sign_tagged_message(self, tagged_message):
		""" Add signature template """
		template_string = self.read_file('cert/sign_sii_xml.tmpl').decode('utf-8')
		tagged_message = tagged_message.replace(self.SIGNATURE_TAG, template_string)
		return self.sign(tagged_message)

	def sign(self, message_with_template_included):
		logger = logging.getLogger()
		"""Should sign a file using a dynamicaly created template, key from PEM and an X509 cert."""
		assert(message_with_template_included)
		# Load the pre-constructed XML template.
		template = etree.fromstring(message_with_template_included)

		# Find the <Signature/> node.
		signature_node = xmlsec.tree.find_node(template, xmlsec.Node.SIGNATURE)

		assert signature_node is not None
		assert signature_node.tag.endswith(xmlsec.Node.SIGNATURE)

		ctx = xmlsec.SignatureContext()
		try:
			ctx.key = xmlsec.Key.from_memory(self.key, format=xmlsec.constants.KeyDataFormatPem)
			ctx.key.load_cert_from_memory(self.cert, format=xmlsec.constants.KeyDataFormatCertPem)
		except xmlsec.Error:
			logger.error("SiiPlugin::sign Key or certificate could not be loaded.")
			return ''

		ctx.sign(signature_node)
		template.remove(xmlsec.tree.find_node(template, xmlsec.Node.SIGNATURE))
		template.insert(1, signature_node)
		return etree.tostring(template, pretty_print=True).decode('utf-8')
