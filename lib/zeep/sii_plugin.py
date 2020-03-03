from zeep import Plugin
from lxml import etree

class SiiPlugin(Plugin):
	def ingress(self, envelope, http_headers, operation):

		return envelope, http_headers

	def egress(self, envelope, http_headers, operation, binding_options):
		operation_body = etree.SubElement(envelope, operation.name)
		print(etree.tostring(operation_body, pretty_print=True))
		return envelope, http_headers
