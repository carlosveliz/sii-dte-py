from lxml import etree
from lxml.etree import QName

from zeep import ns
from zeep.exceptions import SignatureVerificationFailed
from zeep.utils import detect_soap_env
from zeep.wsse.utils import ensure_id, get_security_header

try:
	import xmlsec
except ImportError:
	xmlsec = None

class MemorySignatureOneWay(object):
	"""Sign given SOAP envelope with WSSE sig using given key and cert."""

	def __init__(
	self,
	key_data,
	cert_data,
	password=None,
	signature_method=xmlsec.Transform.RSA_SHA1,
	digest_method=None,
	):
		check_xmlsec_import()

		self.key_data = key_data
		self.cert_data = cert_data
		self.password = password
		self.digest_method = digest_method
		self.signature_method = signature_method

	def apply(self, envelope, headers):
		key = _make_sign_key(self.key_data, self.cert_data, self.password)
		_sign_envelope_with_key(
			envelope, key, self.signature_method, self.digest_method
		)
		return envelope, headers

	def verify(self, envelope):
		""" Avoid checking response """
		return envelope

# SOAP envelope
SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"


def _read_file(f_name):
	with open(f_name, "rb") as f:
		return f.read()

def _make_sign_key(key_data, cert_data, password):
	key = xmlsec.Key.from_memory(key_data, xmlsec.KeyFormat.PEM, password)
	key.load_cert_from_memory(cert_data, xmlsec.KeyFormat.PEM)
	return key

def _make_verify_key(cert_data):
	key = xmlsec.Key.from_memory(cert_data, xmlsec.KeyFormat.CERT_PEM, None)
	return key

class Signature(MemorySignatureOneWay):
	"""Sign given SOAP envelope with WSSE sig using given key file and cert file."""

	def __init__(
		self,
		key_file,
		certfile,
		password=None,
		signature_method=None,
		digest_method=None,
	):
		super(Signature, self).__init__(
			_read_file(key_file),
			_read_file(certfile),
			password,
			signature_method,
			digest_method,
		)

def check_xmlsec_import():
	if xmlsec is None:
		raise ImportError(
			"The xmlsec module is required for wsse.Signature()\n"
			+ "You can install xmlsec with: pip install xmlsec\n"
			+ "or install zeep via: pip install zeep[xmlsec]\n"
		)


def sign_envelope(
	envelope,
	keyfile,
	certfile,
	password=None,
	signature_method=None,
	digest_method=None,
):
	# Load the signing key and certificate.
	key = _make_sign_key(_read_file(keyfile), _read_file(certfile), password)
	return _sign_envelope_with_key(envelope, key, signature_method, digest_method)


def _signature_prepare(envelope, key, signature_method, digest_method):
	"""Prepare envelope and sign."""
	soap_env = detect_soap_env(envelope)

	# Create the Signature node.
	""" Sii uses inclusive C14N """
	signature = xmlsec.template.create(
		envelope,
		xmlsec.Transform.C14N,
		xmlsec.Transform.RSA_SHA1,
	)

	# Add a KeyInfo node with X509Data child to the Signature. XMLSec will fill
	# in this template with the actual certificate details when it signs.
	key_info = xmlsec.template.ensure_key_info(signature)
	x509_data = xmlsec.template.add_x509_data(key_info)
	""" Sii doesn't care about issuer """
	#xmlsec.template.x509_data_add_issuer_serial(x509_data)
	xmlsec.template.x509_data_add_certificate(x509_data)
	""" Sii needs keyinfo """
	xmlsec.template.add_key_value(key_info)

	# Insert the Signature node in the wsse:Security header.
	security = get_security_header(envelope)
	security.insert(0, signature)

	# Perform the actual signing.
	ctx = xmlsec.SignatureContext()
	ctx.key = key
	_sign_node(ctx, signature, envelope.find(QName(soap_env, "Body")), digest_method)
	timestamp = security.find(QName(ns.WSU, "Timestamp"))
	if timestamp != None:
		_sign_node(ctx, signature, timestamp)
	ctx.sign(signature)

	""" Not used by Sii """
	# Place the X509 data inside a WSSE SecurityTokenReference within
	# KeyInfo. The recipient expects this structure, but we can't rearrange
	# like this until after signing, because otherwise xmlsec won't populate
	# the X509 data (because it doesn't understand WSSE).
	#sec_token_ref = etree.SubElement(key_info, QName(ns.WSSE, "SecurityTokenReference"))
	#return security, sec_token_ref, x509_data
	return security, key_info, x509_data


def _sign_envelope_with_key(envelope, key, signature_method, digest_method):
	_, sec_token_ref, x509_data = _signature_prepare(
		envelope, key, signature_method, digest_method
	)
	sec_token_ref.append(x509_data)


def _sign_envelope_with_key_binary(envelope, key, signature_method, digest_method):
	security, sec_token_ref, x509_data = _signature_prepare(
		envelope, key, signature_method, digest_method
	)
	ref = etree.SubElement(
		sec_token_ref,
		QName(ns.WSSE, "Reference"),
		{
			"ValueType": "http://docs.oasis-open.org/wss/2004/01/"
			"oasis-200401-wss-x509-token-profile-1.0#X509v3"
		},
	)
	bintok = etree.Element(
		QName(ns.WSSE, "BinarySecurityToken"),
		{
			"ValueType": "http://docs.oasis-open.org/wss/2004/01/"
			"oasis-200401-wss-x509-token-profile-1.0#X509v3",
			"EncodingType": "http://docs.oasis-open.org/wss/2004/01/"
			"oasis-200401-wss-soap-message-security-1.0#Base64Binary",
		},
	)
	ref.attrib["URI"] = "#" + ensure_id(bintok)
	bintok.text = x509_data.find(QName(ns.DS, "X509Certificate")).text
	security.insert(1, bintok)
	x509_data.getparent().remove(x509_data)


def verify_envelope(envelope, certfile):
	"""Verify WS-Security signature on given SOAP envelope with given cert.
	Expects a document like that found in the sample XML in the ``sign()``
	docstring.
	Raise SignatureVerificationFailed on failure, silent on success.
	"""
	key = _make_verify_key(_read_file(certfile))
	return _verify_envelope_with_key(envelope, key)


def _verify_envelope_with_key(envelope, key):
	soap_env = detect_soap_env(envelope)

	header = envelope.find(QName(soap_env, "Header"))
	if header is None:
		raise SignatureVerificationFailed()

	security = header.find(QName(ns.WSSE, "Security"))
	signature = security.find(QName(ns.DS, "Signature"))

	ctx = xmlsec.SignatureContext()

	# Find each signed element and register its ID with the signing context.
	refs = signature.xpath("ds:SignedInfo/ds:Reference", namespaces={"ds": ns.DS})
	for ref in refs:
		# Get the reference URI and cut off the initial '#'
		referenced_id = ref.get("URI")[1:]
		referenced = envelope.xpath(
			"//*[@wsu:Id='%s']" % referenced_id, namespaces={"wsu": ns.WSU}
		)[0]
		ctx.register_id(referenced, "Id", ns.WSU)

	ctx.key = key

	try:
		ctx.verify(signature)
	except xmlsec.Error:
		# Sadly xmlsec gives us no details about the reason for the failure, so
		# we have nothing to pass on except that verification failed.
		raise SignatureVerificationFailed()

def _sign_node(ctx, signature, target, digest_method=None):
	"""Add sig for ``target`` in ``signature`` node, using ``ctx`` context.
	Doesn't actually perform the signing; ``ctx.sign(signature)`` should be
	called later to do that.
	Adds a Reference node to the signature with URI attribute pointing to the
	target node, and registers the target node's ID so XMLSec will be able to
	find the target node by ID when it signs.
	"""

	# Ensure the target node has a wsu:Id attribute and get its value.
	node_id = ensure_id(target)

	# Unlike HTML, XML doesn't have a single standardized Id. WSSE suggests the
	# use of the wsu:Id attribute for this purpose, but XMLSec doesn't
	# understand that natively. So for XMLSec to be able to find the referenced
	# node by id, we have to tell xmlsec about it using the register_id method.
	ctx.register_id(target, "Id", ns.WSU)

	# Add reference to signature with URI attribute pointing to that ID.
	ref = xmlsec.template.add_reference(
	    signature, digest_method or xmlsec.Transform.SHA1, uri="#" + node_id
	)
	# This is an XML normalization transform which will be performed on the
	# target node contents before signing. This ensures that changes to
	# irrelevant whitespace, attribute ordering, etc won't invalidate the
	# signature.
	""" Sii uses inclusive C14N """
	xmlsec.template.add_transform(ref, xmlsec.Transform.C14N)
