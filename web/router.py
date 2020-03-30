__version__ = '0.1'
import json
import datetime
import uuid
import os
from flask import render_template, jsonify, session, request, redirect, url_for, make_response, Flask
from lib.models.dte import DTEBuidler, DTECAF
from lib.models.sii_token import Token
from lib.pdf_generator import PDFGenerator
from lib.certificate_service import CertificateService
from lib.sii_connector_auth import SiiConnectorAuth

app = Flask(__name__, instance_relative_config=True)

""" Basic key, ensures that is changes everytime with start the application """
epoch = datetime.datetime.utcfromtimestamp(0)
app.secret_key = str(epoch)

""" In memory store, future : database store """
_key_by_uid = {}
_caf_by_uid = {}

def redirect_url(default='index'):
	return request.args.get('next') or \
	request.referrer or \
	url_for(default)

def is_anonymous_authorized_pages(endpoint):
	return (endpoint == 'login' \
	or endpoint == 'static'
	or endpoint == 'index')

@app.before_request
def auth():
	if is_anonymous_authorized_pages(request.endpoint) == False:
		""" Not logged in """
		if 'uid' not in session:
			""" Return HTTP 403, Forbidden and login page """
			return "Not logged in", 403

@app.route('/login', methods=['POST'])
def login():
	if 'RUT' in request.form:
		session['uid'] = uuid.uuid4()
		session['RUT'] = request.form['RUT']
		session['RES'] = request.form['RES']
		session['RES_Date'] = request.form['RES_Date']
		return redirect(redirect_url())
	else:
		return "Missing RUT parameter.", 400

@app.route('/logout', methods=['GET'])
def logout():
	""" Delete session """
	uid = str(session['uid'])
	session.clear()
	try:
		del _key_by_uid[uid]
		del _caf_by_uid[uid]
	except KeyError:
		""" No certificate registered """
		pass
	return redirect(redirect_url('login'))

@app.route('/')
def index():
	return render_template('index.html')

ALLOWED_CERT_EXTENSIONS = ['pfx', 'pem']
def is_valid_cert_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_CERT_EXTENSIONS

ALLOWED_CAF_EXTENSIONS = ['xml', 'caf']
def is_valid_caf_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_CAF_EXTENSIONS

@app.route('/certificate', methods=['POST'])
def set_certificate():
	certificate = request.files['certificate']
	password = request.form['password']

	if is_valid_cert_file(certificate.filename):
		uid = str(session['uid'])
		""" Save in temporary location """
		certificate.filename = str(session['uid']) + '.pfx'
		filepath = 'temp/' + str(certificate.filename)
		certificate.save(filepath)

		""" Extract key and certificate """
		cert = CertificateService(pfx_file_path=filepath, pfx_password=password)
		cert.generate_certificate_and_key()

		""" Store in session """
		_key_by_uid[uid] = { 'key': cert.key, 'cert': cert.certificate }
		session['key_state'] = 'loaded'

		""" Delete """
		os.remove(filepath)
		if cert.key is not None and len(cert.key) > 0:
			return redirect(redirect_url())
		else:
			return "Could not extract key (Invalid password ?)", 400
	else:
		return "Valid file extensions: " + str(ALLOWED_EXTENSIONS), 400

@app.route('/token', methods=['GET'])
def get_token():
	if 'key_state' in session:
		uid = str(session['uid'])
		if uid in _key_by_uid:
			""" Get seed """
			auth = SiiConnectorAuth(module=SiiConnectorAuth.GET_SEED_MODULE_ID)
			seed = auth.get_seed()

			""" Get token """
			auth = SiiConnectorAuth(module=SiiConnectorAuth.GET_TOKEN_MODULE_ID)
			auth.set_key_and_certificate(_key_by_uid[uid]['key'], _key_by_uid[uid]['cert'])

			token_string = auth.get_token(seed)
			token = Token(token_string)

			""" Store in session """
			session['token'] = token.to_json()
			return token.to_json(), 200
		return "Certificate not loaded.", 400

@app.route('/dte',  methods=['POST'])
def set_dte():
	dte = request.json
	return "", 200

@app.route('/caf',  methods=['POST'])
def set_caf():
	uid = str(session['uid'])
	caf = request.files['caf']
	if is_valid_caf_file(caf.filename):
		print("CAF received.")
		_caf_by_uid[uid] = caf.read()
		session['caf'] = caf.filename
	return render_template('index.html'), 200

@app.route('/dte/<string:document_id>/preview',  methods=['GET'])
def generate_preview(document_id):
	""" Get parameters, build HTML and return file """
	return "", 200

@app.route('/document/test/<int:type>/pdf', methods=['GET'])
def generate_pdf(type):
	uid = str(session['uid'])
	""" Get parameters, build PDF and return file """
	pdf = PDFGenerator()
	""" Dump test XML """
	sender_parameters = {}
	receiver_parameters = {}
	specific_header_parameters = {}
	item_list = {}

	""" Read test files """
	with open('test/data/sender.json') as json_file:
		sender_parameters = json.load(json_file)
	with open('test/data/receiver.json') as json_file:
		receiver_parameters = json.load(json_file)
	with open('test/data/items.json') as json_file:
		item_list = json.load(json_file)
	with open('test/data/specifics.json') as json_file:
		specific_header_parameters = json.load(json_file)

	caf = DTECAF(parameters={}, signature='', private_key='')
	caf.load_from_XML_string(_caf_by_uid[uid])

	builder = DTEBuidler()

	_, pretty_dte, dte_object = builder.build(type, sender_parameters, receiver_parameters, specific_header_parameters, item_list, caf)
	pdfFilename, binary_pdf = pdf.generate_binary(dte_object)

	response = make_response(binary_pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = \
	'attachment; filename=%s.pdf' % pdfFilename
	return response

@app.route('/dte/<string:document_id>/sii',  methods=['POST'])
def send_to_sii(document_id):
	""" Send DTE file stored in session at specified ID to SII """
	return "", 200
