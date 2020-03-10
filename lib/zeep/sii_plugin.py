from zeep import Plugin
from lxml import etree
from signxml import XMLSigner, XMLVerifier
import xmlsec
import signxml
import logging

class SiiPlugin(Plugin):
	key = ''
	cert = ''
	SOAP_NS = 'http://schemas.xmlsoap.org/soap/envelope/'
	SII_NS = 'http://DefaultNamespace'

	ns_map = {'soap-env': SOAP_NS, 'sii' : SII_NS}

	def ingress(self, envelope, http_headers, operation):
		""" Hook on received messages """
		return envelope, http_headers

	def egress(self, envelope, http_headers, operation, binding_options):
		logger = logging.getLogger()
		""" Hook on sent messages to override behavior if needed """
		if("getToken" == operation.name):
			""" Remove "ds" namespace """
			logger.info("sii_plugin::egress::getToken behavior.")
			envelope_string = etree.tostring(envelope, pretty_print=True).decode('utf-8')
			""" Set default namsepace to XMLSign, already defined in Signature object """
			envelope_string = envelope_string.replace('ds:', '')
			envelope_string = envelope_string.replace('xmlns:ds="http://www.w3.org/2000/09/xmldsig#"', '')
			envelope = etree.fromstring(envelope_string)
		elif("getSemilla" in operation.name):
			print(str(operation.name))
		else:
			print(str(operation.name))

		return envelope, http_headers

	def test_sign_xmlsec(self, message_with_template_included):
		"""Should sign a file using a dynamicaly created template, key from PEM and an X509 cert."""
		assert(message_with_template_included)
		# Load the pre-constructed XML template.
		template = etree.fromstring(message_with_template_included)

		# Find the <Signature/> node.
		signature_node = xmlsec.tree.find_node(template, xmlsec.Node.SIGNATURE)

		assert signature_node is not None
		assert signature_node.tag.endswith(xmlsec.Node.SIGNATURE)

		ctx = xmlsec.SignatureContext()
		ctx.key = xmlsec.Key.from_memory(self.key, format=xmlsec.constants.KeyDataFormatPem)

		ctx.key.load_cert_from_memory(self.cert, format=xmlsec.constants.KeyDataFormatCertPem)

		ctx.sign(signature_node)
		template.remove(xmlsec.tree.find_node(template, xmlsec.Node.SIGNATURE))
		template.insert(0, signature_node)
		return etree.tostring(template, pretty_print=True).decode('utf-8')

	def _sign(self, etree_data_to_sign, key, cert):
		""" SII Specifications : SHA1 / CanonicalizationMethod = REC-XML-cl4n inclusive """
		signed_data = XMLSigner(method=signxml.methods.enveloped,
								signature_algorithm=u'rsa-sha1',
								digest_algorithm=u'sha1',
								c14n_algorithm=u'http://www.w3.org/TR/2001/REC-xml-c14n-20010315'
								).sign(etree_data_to_sign, key=key, cert=cert)
		return signed_data

	def sign_seed(self, seed_message):
		seed_message_etree = etree.fromstring(seed_message)
		signed_etree = self._sign(seed_message_etree, self.key, self.cert)
		signed_seed = etree.tostring(signed_etree, pretty_print=True).decode('utf-8')
		signed_seed = '<?xml version="1.0"?> ' + '\n\r' + signed_seed
		return signed_seed

	def _remove_default_namespace(self, etree_data, default_namespace):
		string_data = etree.tostring(etree_data).decode('utf-8')
		string_data = string_data.replace('xmlns:' + default_namespace, 'xmlns')
		string_data = string_data.replace(default_namespace + ':', '')
		data = etree.fromstring(string_data)
		return data
