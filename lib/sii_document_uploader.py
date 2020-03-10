import requests
from instance.config import APPLICATION_NAME, REFERER

class SiiDocumentUploader():
	""" State seems to be at least 3 digits """
	REGEX_MATCH_STATE = r"<ESTADO>(\d{2,})</ESTADO>"
	_token = ''
	""" https://maullin.sii.cl/cgi_dte/UPL/DTEUpload """
	_url = ''

	def __init__(self, token, url)
		self._token = token
		self._url = url

	def send_document(self, user_rut, dest_rut, sii_document)
		#POST /cgi_dte/UPL/DTEUpload
		#HTTP/1.0^M Accept: image/gif, image/x-xbitmap, image/jpeg, image/pjpeg, application/vnd.ms-powerpoint, application/ms-excel, application/msword, */*
		#Referer:http://empresaabc.cl/test.html
		#Accept-Language: es-cl
		#Content-Type: multipart/form-data: boundary=7d23e2a11301c4
		#Accept-Encoding: gzip, deflate
		#User-Agent: Mozilla/4.0 (compatible; PROG 1.0; Windows NT 5.0; YComp 5.0.2.4)
		#Host: https://maullin.sii.cl
		#Content-Length: 10240
		#Connection: Keep-Alive
		#Cache-Control: no-cache
		#Cookie: TOKEN=YZD0II2ApZjlM
		payload = { \
			'rutSender': user_rut, \
			'dvSender': user_rut, \
			'rutCompany': dest_rut, \
			'dvCompany': dest_rut, \
			'archivo': open('file_name.pdf', 'rb')
		}
		headers = { \
				'Content-type': 'multipart/form-data', \
				'Accept-Charset': 'UTF-8', \
				'User-Agent: Mozilla/4.0 (compatible; PROG 1.0; ' + APPLICATION_NAME + ')', \
				'Referer: ' + REFERER, \
				'Cookie: TOKEN=' + self._token
		}
		r = requests.post(self._url, data=payload, headers=headers)
