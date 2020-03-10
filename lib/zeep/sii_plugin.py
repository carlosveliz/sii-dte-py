from zeep import Plugin
from lxml import etree
import xmlsec
import logging

class SiiPlugin(Plugin):
	key = ''
	cert = ''

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
