__version__ = '0.1'
import json
import datetime
import uuid
from flask import render_template, jsonify, session, request, redirect, url_for, Flask
from lib.models.dte import DTEBuidler
from lib.pdf_generator import PDFGenerator
from lib.certificate_service import CertificateService
from lib.sii_connector_auth import SiiConnectorAuth

app = Flask(__name__, instance_relative_config=True)

""" Basic key, ensures that is changes everytime with start the application """
epoch = datetime.datetime.utcfromtimestamp(0)
app.secret_key = str(epoch)

def is_anonymous_authorized_pages(endpoint):
	return (endpoint == 'login' \
	or endpoint == 'static')

@app.before_request
def auth():
	if is_anonymous_authorized_pages(request.endpoint) == False:
		""" Not logged in """
		if 'uid' not in session:
			""" Return HTTP 403, Forbidden and login page """
			return "Not logged in", 403

@app.route('/login', methods=['GET'])
def login():
	session['uid'] = uuid.uuid4()

@app.route('/logout', methods=['POST'])
def logout():
	""" Delete session """
	del session['key']
	del session['cert']
	del session['uid']
	return "", 200

@app.route('/')
def index():
	return "Running", 200

ALLOWED_EXTENSIONS = ['pfx', 'pem']
def is_valid_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

@app.route('/certificate', methods=['POST'])
def set_certificate():
	certificate = request.files['certificate']
	password = request.form['password']

	if is_valid_file(certificate.filename):
		""" Save in temporary location """
		certificate.filename = 'c-' + str(session['uid'])
		filepath = '../temp/' + str(certificate.filename)
		certificate.save(filepath)

		""" Extract key and certificate """
		cert = CertificateService(pfx_file_path=filepath, pfx_password=password)
		cert.generate_certificate_and_key()

		""" Store in session """
		session['key'] = cert.key
		session['cert'] = cert.certificate

		""" Delete """
		os.remove(filepath)
	else:
		return "Valid file extensions: " + str(ALLOWED_EXTENSIONS), 400

@app.route('/token', methods=['GET'])
def get_token():
	if 'key' not in session or 'cert' not in session:
		""" Get seed """
		auth = SiiConnectorAuth(module=SiiConnectorAuth.GET_SEED_MODULE_ID)
		seed = auth.get_seed()

		""" Get token """
		auth = SiiConnectorAuth(module=SiiConnectorAuth.GET_TOKEN_MODULE_ID)
		auth.set_key_and_certificate(cert.key, cert.certificate)

		token_string = auth.get_token(seed)
		token = Token(token_string)

		""" Store in session """
		session['token'] = token
		return token.to_json(), 200
	else:
		return "Certificate not loaded.", 400

@app.route('/dte',  methods=['POST'])
def set_dte():
	dte = request.json
	return "", 200

@app.route('/dte/<string:document_id>/preview',  methods=['GET'])
def generate_preview(document_id):
	""" Get parameters, build PDF and return file """
	return "", 200

@app.route('/pdf', methods=['POST'])
def generate_pdf():
	""" Get parameters, build PDF and return file """
	return "", 200

@app.route('/dte/<string:document_id>/sii',  methods=['POST'])
def send_to_sii(document_id):
	""" Send DTE file stored in session at specified ID to SII """
	return "", 200
