#!/usr/bin/env python
import datetime
from lxml import etree
from ..zeep.sii_plugin import SiiPlugin

"""
General format :

<DTE version=1.0”>
 <Documento ID=””>
	 <Encabezado>... </Encabezado>
	 <DetalleFactura>... </DetalleFactura>
	 <DescuentoRecargoGlobal>... </DescuentoRecargoGlobal>
	 <Referencia>... </Referencia>
	 <TED>... </TED> /* Timbre Electrónico DTE
	 <TmstFirma> ... </TmstFirma> /* TimeStamp firma del DTE
 </Documento>
<Signature>  	Firma digital sobre
  <Documento>... </Documento>
  </Signature>

</DTE>


"""

DTE_SII_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

class DTEPerson:
	_type = 0
	__types = ['Receiver', 'Sender']
	_parameters = [];

	__markup = {'Receiver': {'Type':'Receptor',
							'RUT':'RUTRecep',
							'Name':'RznSocRecep',
							'Activity':'GiroRecep',
							'Address':'DirRecep',
							'Comune':'CmnaRecep',
							'City':'CiudadRecep'},
				'Sender': {'Type':'Emisor',
				 			'RUT':'RUTEmisor',
							'Name':'RznSoc',
							'Activity':'GiroEmis',
							'Address':'DirOrigen',
							'Comune':'CmnaOrigen',
							'City':'CiudadOrigen',
							'Acteco':'Acteco'}
				}

	"""
	Acteco
	Se acepta un máximo de 4 Códigos de actividad económica del emisor del DTE.
	Se puede incluir sólo el código que corresponde a la transacción
	"""

	def __init__(self, type, parameters):
		self._type = type
		self._parameters = parameters

	def get_attr(self, attr):
		return self._parameters[attr]

	def dump(self):
		outside_markup = self.__markup[self.__types[self._type]]['Type']
		dumped = '<' + outside_markup + '>'

		for param in self._parameters:
			markup = self.__markup[self.__types[self._type]][param]
			value = self._parameters[param]
			dumped = dumped + '<' + markup + '>' + value + '</' + markup + '>'

		dumped = dumped + '</' + outside_markup + '>'
		return dumped

	def get_property_by_markup(self, type, search_markup):
		for property, markup in self.__markup[self.__types[type]].items():
			if markup == search_markup:
				return property

	def from_xml_parameters(self, type, xml_parameters):
		parameters = {}

		for markup in xml_parameters:
			prop = self.get_property_by_markup(type, markup)
			if prop is not None:
				parameters[prop] = xml_parameters[markup]

		self._parameters = parameters
		return parameters

class DTEHeader:
	""" Document identity, composed of sender, reciber information, document type, and total amount """
	sender = DTEPerson(1, None)
	receiver = DTEPerson(0, None)
	dte_document_type = 0
	dte_document_number = 0
	_dte_export_type = 0
	_dte_export_indicator = 0
	_dte_payment_method = 0
	_dte_expiry_date = 0
	_net_amount = 0
	_tax_rate = 0
	_taxes = 0
	total_amount = 0

	_specifics = None
	totales = {}

	__valid_document_types = {
	33: 'Factura Electrónica',
	34: 'Factura No Afecta o Exenta Electrónica',
	43: 'Liquidación-Factura Electrónica',
	46: 'Factura de Compra Electrónica',
	52: 'Guía de Despacho Electrónica',
	56: 'Nota de Débito Electrónica',
	61: 'Nota de Crédito Electrónica',
	110: 'Factura de Exportación',
	111: 'Nota de Débito de Exportación',
	112: 'Nota de Crédito de Exportación'
	}


	"""
	MovementType <IndTraslado>
	1:  Operación constituye
	2:  Ventas por efectuar
	3:  Consignaciones
	4:  Entrega gratuita
	5: Traslados internos
	6: Otros traslados no venta
	7: Guía de devolución
	8: Traslado para exportación. (no venta)
	9: Venta para exportación
	"""
	"""
	ExpeditionType <TipoDespacho>
	1: Despacho por cuenta del receptor del documento (cliente o vendedor  en caso de Facturas de compra.)
	2: Despacho por cuenta del  emisor a instalaciones del  cliente
	3: Despacho por cuenta del emisor a otras instalaciones (Ejemplo: entrega en Obra)
	"""
	"""
	PrintedFormat <TpoImpresion>
	T: Ticket
	N: Normal
	"""

	__specifics_by_document_type = {52: {'MovementType':'IndTraslado',
										'ExpeditionType':'TipoDespacho',
										'PrintedFormat': 'TpoImpresion'
										},
									33: {}
								}
	comment = ''

	def __init__(self, sender, receiver, document_type, document_number, payment_method, expiry_date, specific_parameters, totales):
		""" specific_parameters parameter should contains document type based parameters """
		assert(document_type in self.__valid_document_types)
		self.sender = sender
		self.receiver = receiver
		self.dte_document_type = document_type
		self.dte_document_number = document_number
		self._dte_payment_method = payment_method
		self._dte_expiry_date = expiry_date
		self._specifics = specific_parameters
		self.totales = totales

		try:
			self.comment = specific_parameters['Comment']
		except:
			pass

	def dump_specifics(self):
		dumped = ''
		for param in self._specifics:
			try:
				markup = self.__specifics_by_document_type[self.dte_document_type][param]
				value = self._specifics[param]
				dumped = dumped + '<' + markup + '>' + str(value) + '</' + markup + '>'
			except:
				continue

		return dumped

	def dump(self):
		return '<Encabezado>' + self.dump_document_identification() + \
		self.sender.dump()  + \
		self.receiver.dump() + \
		self.dump_totales() + \
		 '</Encabezado>'

	def dump_totales(self):
		return '<Totales><MntNeto>' + str(self.totales['Net']) + '</MntNeto>' + \
						'<TasaIVA>' + str(self.totales['Rate']) + '</TasaIVA>' + \
						'<IVA>' + str(self.totales['IVA']) + '</IVA>' + \
						'<MntTotal>' + str(self.totales['Total']) + '</MntTotal>' + \
		 			'</Totales>'

	def dump_document_identification(self):
		return '<IdDoc>' + self.dump_document_type() + \
						self.dump_document_number() + \
						self.dump_issue_date() + \
						self.dump_specifics() + \
						self.dump_payment_method() + \
						self.dump_expiry_date() + \
						'</IdDoc>'

	def dump_document_number(self):
		return '<Folio>'+ str(self.dte_document_number) +'</Folio>'

	def dump_document_type(self):
		return '<TipoDTE>' + str(self.dte_document_type) + '</TipoDTE>'

	def dump_issue_date(self):
		return '<FchEmis>' + str(datetime.datetime.now().strftime(DTE_SII_DATE_FORMAT)) + '</FchEmis>'

	def dump_payment_method(self):
		return '<FmaPago>' + str(self._dte_payment_method) + '</FmaPago>'

	def dump_expiry_date(self):
		return '<FchVenc>' + str(self._dte_expiry_date) + '</FchVenc>'

	def get_property_by_markup(self, document_type, search_markup):
		for property, markup in self.__specifics_by_document_type[document_type].items():
			if markup == search_markup:
				return property

	def load_specifics_from_xml_parameters(self, document_type, parameters):
		for i in parameters:
			property = self.get_property_by_markup(document_type, i)
			if property is not None:
				self._specifics[property] = parameters[i]

class DTEItems:
	"""
	'CodeType':'TpoCodigo',
		EAN13, PLU, DUN14, INT1, INT2, EAN128, etc.
	"""

	"""
	'Extension':'IndExe'
	1: No afecto o exento de IVA  (10)
	2: Producto o servicio no es facturable
	3: Garantía de depósito por envases (Cervezas, Jugos, Aguas Minerales, Bebidas Analcohólicas u otros autorizados por Resolución especial)
	4: Ítem No Venta. (Para facturas y  guías de despacho (ésta última con Indicador Tipo de Traslado de Bienes igual a 1)  y este ítem no será facturando
	5: Ítem a rebajar. Para guías de despacho NO VENTA que rebajan guía anterior. En el área de  referencias se debe indicar la guía anterior.
	6: Producto o servicio no facturable negativo (excepto en liquidaciones-factura)
	"""

	"""
	'ItemPrice':'MontoItem'
	(Precio Unitario  * Cantidad ) – Monto Descuento + Monto Recargo
	"""

	__properties_by_document_type = {52: {},
									33: {},
									43: {'LiqDocType':'TpoDocLiq'},
									0: { 'Index':'NroLinDet',
										'CodeType':'TpoCodigo',
										'Code':'VlrCodigo',
										'Extension':'IndExe',
										'Name':'NmbItem',
										'Description':'DscItem',
										'Quantity':'QtyItem',
										'Unit':'UnmdItem',
										'UnitPrice':'PrcItem',
										'ItemPrice':'MontoItem'
										}
								}

	_items = None
	_document_type = 0

	def __init__(self, document_type, items):
		self._document_type = document_type
		self._items = items

	def dump_items(self):
		dumped = ''
		index = 0
		index_markup = self.__properties_by_document_type[0]['Index']
		for item_key in self._items:
			""" Get item """
			item = self._items[item_key]
			if item is not None:
				dumped = dumped + '<Detalle>'
				index = index + 1
				dumped = dumped + '<' + index_markup + '>' + str(index) + '</' + index_markup + '>'

				""" Build with common properties """
				for prop in item:
					try:
						markup = self.__properties_by_document_type[0][prop]
						value = item[prop]
						dumped = dumped + '<' + markup + '>' + str(value) + '</' + markup + '>'
					except:
						pass
				""" Specific properties """
				for prop in item:
					try:
						markup = self.__properties_by_document_type[self._document_type][prop]
						value = item[prop]
						dumped = dumped + '<' + markup + '>' + str(value) + '</' + markup + '>'
					except:
						pass
				dumped = dumped + '</Detalle>'
		return dumped

	def dump_totales(self, totales):
		dump = '<MntNeto>' + str(totales['Net']) + '</MntNeto>'
		dump = dump + '<TasaIVA>' + str(totales['Rate']) + '</TasaIVA>'
		dump = dump + '<IVA>' + str(totales['IVA']) + '</IVA>'
		dump = dump + '<MntTotal>' + str(totales['Total']) + '</MntTotal>'

		return dump

	def get_totales(self, iva_rate):
		totales = {}
		totales['Net'] = 0

		for item_key in self._items:
			totales['Net'] = int(totales['Net']) + int(self._items[item_key]['ItemPrice'])

		totales['Rate'] = iva_rate
		totales['IVA'] = totales['Net'] * iva_rate
		totales['Total'] = totales['IVA'] + totales['Net']

		return totales

	def get_item_list_for_template(self):
		return self._items

	def get_first_item_description(self):
		first_key = list(self._items.keys())[0]
		try:
			return self._items[first_key]['Description']
		except:
			return self._items[first_key]['Name']

	def get_property_by_markup(self, document_type, search_markup):
		for property, markup in self.__properties_by_document_type[document_type].items():
			if markup == search_markup:
				return property
		""" Common properties """
		for property, markup in self.__properties_by_document_type[0].items():
			if markup == search_markup:
				return property

	def load_from_xml_parameters(self, document_type, parameters):
		self._items = {}
		index = 0
		for i in parameters:
			item = parameters[i]
			for elem in item:
				property = self.get_property_by_markup(document_type, elem)
				if property == "Index":
					index = item[elem]
					self._items[index] = {}
				if property is not None:
					self._items[index][property] = item[elem]

	def dump(self):
		return self.dump_items()

class DTEReference:
	_code = ''
	_dte_document_type = 0

	def dump(self):
		return '<DTEReference></DTEReference>'

class DTECover:

	"""
	<Caratula version="1.0">
		<RutEmisor>76087419-1</RutEmisor>
		<RutEnvia>22926257-2</RutEnvia>
		<RutReceptor>55555555-5</RutReceptor>
		<FchResol>2014-08-22</FchResol>
		<NroResol>80</NroResol>
		<TmstFirmaEnv>2020-03-19T11:22:45</TmstFirmaEnv>
		<SubTotDTE>
			<TpoDTE>110</TpoDTE>
			<NroDTE>1</NroDTE>
		</SubTotDTE>
	</Caratula>
	"""
	_dtes = {}
	""" Resolution must be {'Date':'YYYY-MM-DD', 'Number': 'XXXX' } """
	_resolution = {}
	""" User must be {'RUT' : 'XXXXXXXX-X'} """
	_user = {}

	def __init__(self, dtes, resolution, user):
		self._dtes = dtes
		self._resolution = resolution
		self._user = user

	def dump(self):
		dumped = '<Caratula version="1.0">' + self.sender() + self.receiver() + \
				self.resolution() + self.signature_date() + self.dte_details() + '</Caratula>'
		return dumped

	def sender(self):
		return '<RutEmisor>' + self.dte_sender() + '</RutEmisor>' + \
				'<RutEnvia>' + self._user['RUT'] + '</RutEnvia>'

	def receiver(self):
		return '<RutReceptor>' + self.dte_receiver() + '</RutReceptor>'

	def resolution(self):
		return '<FchResol>' + self._resolution['Date'] + '</FchResol>' + \
				'<NroResol>' + self._resolution['Number'] + '</NroResol>'

	def signature_date(self):
		return '<TmstFirmaEnv>' + datetime.datetime.now().strftime(DTE_SII_DATE_FORMAT) + '</TmstFirmaEnv>'

	def dte_type(self):
		type = ''
		for dte in self._dtes:
			doc = self._dtes[dte]
			if type == '':
				type = doc.get_document_type()
			else:
				if type != doc.get_document_type():
					raise ValueError('Multiple document type found. Should be only one document type by Set.')
		return type

	def dte_sender(self):
		sender = ''
		for dte in self._dtes:
			doc = self._dtes[dte]
			if sender == '':
				sender = doc.get_document_sender()
			else:
				if sender != doc.get_document_sender():
					raise ValueError('Multiple document sender found. Should be only one document sender by Set.')
		return sender

	def dte_receiver(self):
		receiver = ''
		for dte in self._dtes:
			doc = self._dtes[dte]
			if receiver == '':
				receiver = doc.get_document_receiver()
			else:
				if receiver != doc.get_document_receiver():
					raise ValueError('Multiple document receiver found. Should be only one document receiver by Set.')
		return receiver

	def dte_quantity(self):
		return len(self._dtes)

	def dte_details(self):
		return '<SubTotDTE><TpoDTE>' + str(self.dte_type()) + '</TpoDTE><NroDTE>' + str(self.dte_quantity()) + '</NroDTE></SubTotDTE>'

class DTECAF:
	embedded_private_key = ''
	_parameters = None
	_signature = ''
	__markup = { 'RUT':'RE',
					'Name':'RS',
					'Type':'TD',
					'_From':'D',
					'_To':'H',
					'FechaAuthorization':'FA',
					'_RSAPrivateKeyModule':'M',
					'_RSAPrivateKeyExp':'E',
					'KeyId':'IDK',
					'_Signature' :'',
					'_PrivateKey': '',
					'_EmbeddedSignature': 'FRMA',
					'_RSAPrivateKey': 'RSASK',
					'_RSAPublicKey': 'RSAPUBK'
					}
	algorithm = 'SHA1withRSA'
	def __name__(self):
		return 'DTECAF'

	def __init__(self, signature, parameters, private_key=''):
		self._parameters = parameters
		self._signature = signature
		if('_RSAPrivateKey' in parameters):
			self.embedded_private_key = parameters['_RSAPrivateKey']
		else:
			self.embedded_private_key = private_key

	def dump(self):
		dumped = '<AUTORIZACION><CAF version="1.0"><DA>'
		for param in self._parameters:
			markup = self.__markup[param]
			if '_' in param:
				""" Should not be printed """
				continue
			value = self._parameters[param]
			dumped = dumped + '<' + markup + '>' + value + '</' + markup + '>'
		""" Add range """
		dumped = dumped + '<RSAPK><M>' + self._parameters['_RSAPrivateKeyModule'] + '</M><E>'+ self._parameters['_RSAPrivateKeyExp'] +'</E></RSAPK>'
		dumped = dumped + '<RNG><D>' + self._parameters['_From'] + '</D><H>'+ self._parameters['_To'] +'</H></RNG>'
		dumped = dumped + '</DA>'
		dumped = dumped + '<FRMA algoritmo="' + self.algorithm + '">' + self._parameters['_EmbeddedSignature'] + '</FRMA>'
		dumped = dumped + '</CAF></AUTORIZACION>'

		return dumped

	def load_from_XML(self, filepath):
		print("Loading CAF from xml")
		tree = etree.parse(filepath)
		return self.load_from_etree(tree)

	def get_property_by_markup(self, search_markup):
		for property, markup in self.__markup.items():
			if markup == search_markup:
				return property

	def load_from_etree(self, tree):
		""" Load from etree object """
		for elem in tree.iter():
			property = self.get_property_by_markup(elem.tag)
			if property is not None:
				self._parameters[property] = elem.text
			""" Get signature algorithm """
			if elem.tag == 'FRMA':
				self.algorithm = elem.attrib['algoritmo']

		self.embedded_private_key = self._parameters['_RSAPrivateKey']

	def load_from_xml_parameters(self, parameters):
		""" Load from dictionnary of parameters [markup => value] """
		for elem in parameters:
			property = self.get_property_by_markup(elem)
			if property is not None:
				self._parameters[property] = parameters[elem]

	def get_document_type(self):
		""" Returns SII document type """
		return int(self._parameters['Type'])

class DTE:
	""" Envio DTE """
	""" From documentation, every document should have this parts : """
	"""
	A:- Datos de encabezado: corresponden a la identificación del documento, información del emisor, información del receptor y monto total de la transacción.
	B:- Detalle por Ítem: En esta zona se debe detallar una línea por cada Ítem. Se debe detallar cantidad, valor, descuentos y recargos por ítem,  impuestos adicionales y valor neto. En el caso de la Liquidación-Factura, se detallan los datos de los documentos liquidados.
	C:- Descuentos y Recargos: Esta zona se utiliza para especificar descuentos o recargos que afectan al total del documento y que no se requiere especificar ítem a ítem.
	D:- Información de Referencia: En esta zona se deben detallar los documentos de referencia, por ejemplo se debe identificar la Guía de Despacho que se está facturando o la Factura que se está modificando con una Nota de crédito o de débito.
	E:- Comisiones y Otros Cargos: Obligatoria para Liquidación Factura y opcional para Factura de Compra y Nota de Crédito/Débito que corrijan operaciones relacionadas con Facturas de Compra.
	F:- Timbre Electrónico SII: Firma electrónica sobre la información representativa del documento para permitir la validación del documento impreso.
	G:- Fecha y hora de la firma electrónica H.- Firma Electrónica sobre toda la información anterior para garantizar la integridad del DTE enviado al SII
	"""
	_header = None
	_items = None
	_discount = ''
	_reference = [] #DTEReference
	_other_charges = [] #DTEItems()
	_sii_signature = None
	_timestamp = datetime.datetime.now().strftime(DTE_SII_DATE_FORMAT)
	_caf = None
	_document_id = ''
	_ted = ''

	def __init__(self, header, items, discount, reference, other, signature, timestamp, caf=None, signer=None, ted=''):
		self._header = header
		self._items = items
		self._discount = discount
		self._reference = reference
		self._other_charges = other
		self._sii_signature = signature
		self._timestamp = timestamp
		self._caf = caf
		self._document_id = 'T' + str(self._header.dte_document_type) + 'I' + str(self._header.dte_document_number)
		self._signer = signer
		self._ted = ted

	def generate_ted(self):
		""" If not already generated """
		if self._ted == '':
			caf_private_key = ''
			document_data = '<DD>' + \
					  '<RE>' + self._header.sender.get_attr('RUT') + '</RE>' + \
					  '<TD>' + str(self._header.dte_document_type) + '</TD>' + \
					  '<F>' + str(self._header.dte_document_number) + '</F>' + \
					  '<FE>' + str(self._timestamp) + '</FE>' + \
					  '<RR>' + self._header.receiver.get_attr('RUT') + '</RR>' + \
					  '<RSR>' + self._header.receiver.get_attr('Name') + '</RSR>' + \
					  '<MNT>' + str(self._header.total_amount) + '</MNT>' + \
					  '<IT1>' + self._items.get_first_item_description() + '</IT1>' + \
					  self._caf.dump() + \
					  '<TSTED>' + str(datetime.datetime.now().strftime(DTE_SII_DATE_FORMAT)) + '</TSTED>' + \
					  '</DD>'

			signature = self.sign(document_data, self._caf.embedded_private_key)
			ted = '<TED version="1.0">' + \
				document_data + \
			  '<FRMT algoritmo="SHA1withRSA">' + signature + '</FRMT>' + \
			  '</TED>'

			self._ted = ted
			return ted
		else:
			return self._ted

	def get_document_type(self):
		return str(self._header.dte_document_type)

	def get_document_sender(self):
		return self._header.sender.get_attr('RUT')

	def get_document_receiver(self):
		return self._header.receiver.get_attr('RUT')

	def sign(self, data, key, algorithm='SHA1withRSA'):
		""" If there a signer module loaded """
		if self._signer is not None:
			self._signer.key = key
			sign = self._signer.sign_with_algorithm(data, algorithm)
			return sign
		else:
			""" Sign """
			import xmlsec
			import base64
			ctx = xmlsec.SignatureContext()
			ctx.key = xmlsec.Key.from_memory(key, format=xmlsec.constants.KeyDataFormatPem)
			data = data.replace('\n', ' ').replace('\r', '').replace('\t', '').replace('> ', '>').replace(' <', '<')

			data = bytes(data, 'ISO-8859-1')

			sign = ctx.sign_binary(data, xmlsec.constants.TransformRsaSha1)
			""" To base 64 and back """
			base64_encoded_data = base64.b64encode(sign)
			return base64_encoded_data.decode('ISO-8859-1')

	def dump(self):
		return '<DTE version="1.0">' + self.dump_document_only() + '</DTE>'

	def dump_document_only(self):
		ted = ''
		if self._ted == '':
			""" Generate """
			ted = self.generate_ted()
		else:
			""" Preloaded """
			ted = self._ted
		return '<Documento ID="' + self._document_id + '">' + self._header.dump() + self._items.dump() + ted + '</Documento>'

	def to_template_parameters(self):
		dict = {
				'Header': {
					'Specifics': self._header._specifics
				},
				'Sender': {
							'RUT':self._header.sender.get_attr('RUT'),
							'Name':self._header.sender.get_attr('Name'),
							'Activity':self._header.sender.get_attr('Activity'),
							'Address':self._header.sender.get_attr('Address'),
							'Address2':'',
							'City':self._header.sender.get_attr('City'),
							'Phone':''
							},
				'DocumentNumber': self._header.dte_document_number,
				'SII' : 'SANTIAGO CENTRO',
				'Receiver': {
							'RUT':self._header.receiver.get_attr('RUT'),
							'Name':self._header.receiver.get_attr('Name'),
							'Activity':self._header.receiver.get_attr('Activity'),
							'Address':self._header.receiver.get_attr('Address'),
							'Address2':'',
							'City':self._header.sender.get_attr('City'),
							'Phone':''
				},
				'Details': self._items.get_item_list_for_template(),
				'Comment': self._header.comment,
				'Totales': self._header.totales
		}

		return dict

class DTEPayload:
	""" EnvioDTE """

	def __init__(self, dtes, cover, user):
		self._dtes = dtes
		self._cover = cover

	def dump(self):
		set = '<SetDTE ID="SetDoc">' + \
				self._cover.dump() + \
				self.dump_documents() + '</SetDTE>'
		dumped = '<?xml version="1.0" encoding="ISO-8859-1"?>' + \
			'<EnvioDTE xmlns="http://www.sii.cl/SiiDte" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sii.cl/SiiDte EnvioDTE_v10.xsd" version="1.0">' + \
			 set + SiiPlugin.SIGNATURE_TAG + '</EnvioDTE>'

		return dumped

	def dump_documents(self):
		dumped = ''
		for doc in self._dtes:
			dumped = dumped + self._dtes[doc].dump()

		return dumped

class DTEBuidler:
	__iva_by_type = {33: 0.19, 52: 0.19, 34: 0}
	__object_type_by_tag = { '{http://www.sii.cl/SiiDte}RutEmisor':'RE',
					'Name':'RS',
					'Type':'TD',
					'_From':'D',
					'_To':'H',
					'FechaAuthorization':'FA',
					'_RSAPrivateKeyModule':'M',
					'_RSAPrivateKeyExp':'E',
					'KeyId':'IDK',
					'_Signature' :'',
					'_PrivateKey': '',
					'_EmbeddedSignature': 'FRMA',
					'_RSAPrivateKey': 'RSASK',
					'_RSAPublicKey': 'RSAPUBK'
					}


	def build(self, type, sender, receiver, header, items, caf):
		sender_object = DTEPerson(1, sender)
		receiver_object = DTEPerson(0, receiver)
		items_object = DTEItems(type, items)
		iva_rate = self.__iva_by_type[type]
		header_object = DTEHeader(sender_object, receiver_object, type, 1, 1, datetime.datetime.now().strftime(DTE_SII_DATE_FORMAT), header, items_object.get_totales(iva_rate))

		if isinstance(caf, DTECAF):
			""" Is already an object """
			caf_object = caf
		else:
			""" Build object """
			caf_object = DTECAF(parameters=caf, signature=signature, private_key=private_key)
			signature = caf['_Signature']
			private_key = caf['_PrivateKey']

		dte = DTE(header_object, items_object, '', '', '', '', '',caf=caf_object)

		dte_etree = etree.fromstring(dte.dump())
		pretty_dte = etree.tostring(dte_etree, pretty_print=True).decode('UTF-8')
		return dte_etree, pretty_dte, dte

	def from_file(self, path):
		tree = etree.parse(path)
		root = tree.getroot()

		return self.load_from_etree(root)

	def iterate_recurs_etree(self, tree, parameters):
		items = 0
		for child in tree:
			""" Remove SII general tag """
			tag = child.tag.replace('{http://www.sii.cl/SiiDte}','')
			if len(child) > 1:
				""" Extract elements """
				if tag == 'Encabezado':
					header = {}
					parameters['Header'] = {}
					parameters['Header'] = self.iterate_recurs_etree(child, header)
				if tag == 'Emisor':
					sender = {}
					parameters['Sender'] = {}
					parameters['Sender'] = self.iterate_recurs_etree(child, sender)
				if tag == 'Receptor':
					receiver = {}
					parameters['Receiver'] = {}
					parameters['Receiver'] = self.iterate_recurs_etree(child, receiver)
				if tag == 'Detalle':
					item = {}
					if items == 0:
						parameters['Items'] = {}
					parameters['Items'][items] = {}
					parameters['Items'][items] = self.iterate_recurs_etree(child, item)
					items = items + 1
				if tag == 'CAF':
					caf = {}
					parameters['CAF'] = {}
					parameters['CAF'] = self.iterate_recurs_etree(child, caf)
				if tag == 'TED':
					ted = {}
					parameters['TED'] = {}
					parameters['TED'] = self.iterate_recurs_etree(child, ted)
					parameters['TED']['Dump'] = etree.tostring(child).decode('UTF-8')
				if tag == 'Totales':
					totals = {}
					parameters['Totals'] = {}
					parameters['Totals'] = self.iterate_recurs_etree(child, totals)
				else:
					self.iterate_recurs_etree(child, parameters)
			else:
				parameters[tag] = child.text

		return parameters

	def load_from_etree(self, tree):
		""" Build parameters """
		parameters = {}
		parameters = self.iterate_recurs_etree(tree, parameters)
		""" Get individual set """
		sender_parameters = parameters['Sender']
		receiver_parameters = parameters['Receiver']
		items_parameters = parameters['Items']
		caf_parameters = parameters['CAF']
		ted_parameters = parameters['TED']
		header_parameters = parameters['Header']
		""" Get dumped TED """
		dumped_ted = parameters['TED']['Dump']
		""" Totals """
		totals_parameters = parameters['Totals']
		""" Build objects """
		""" Send and receiver """
		sender = DTEPerson(1, None)
		sender.from_xml_parameters(1, sender_parameters)
		receiver = DTEPerson(0, None)
		receiver.from_xml_parameters(0, receiver_parameters)
		""" CAF """
		caf = DTECAF(parameters={}, signature='', private_key='')
		caf.load_from_xml_parameters(caf_parameters)
		""" Get document type """
		document_type = caf.get_document_type()
		document_number = int(ted_parameters['F'])
		""" Items """
		items = DTEItems(document_type=document_type, items={})
		items.load_from_xml_parameters(document_type=document_type, parameters=items_parameters)
		""" Get IVA rate """
		iva_rate = self.__iva_by_type[document_type]

		""" Build header """
		header = DTEHeader(sender, receiver, document_type, document_number, 1, datetime.datetime.now().strftime(DTE_SII_DATE_FORMAT), {}, items.get_totales(iva_rate))
		header.load_specifics_from_xml_parameters(document_type, header_parameters)
		""" Build final DTE """
		dte = DTE(header, items, '', '', '', '', '',caf=caf, ted=dumped_ted)

		""" Extract tree and dump pretty XML """
		dte_etree = etree.fromstring(dte.dump())
		pretty_dte = etree.tostring(dte_etree, pretty_print=True).decode('UTF-8')

		return dte_etree, pretty_dte, dte
