#!/usr/bin/env python
import datetime
from lxml import etree

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

	def __init__(self, sender, receiver, document_type, document_number, payment_method, expiry_date, specific_parameters):
		""" specific_parameters parameter should contains document type based parameters """
		assert(document_type in self.__valid_document_types)
		self.sender = sender
		self.receiver = receiver
		self.dte_document_type = document_type
		self.dte_document_number = document_number
		self._dte_payment_method = payment_method
		self._dte_expiry_date = expiry_date
		self._specifics = specific_parameters
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
		return '<Totales>' + '<MntNeto>' + str(self._net_amount) + '</MntNeto>' + \
						'<TasaIVA>' + str(self._tax_rate) + '</TasaIVA>' + \
						'<IVA>' + str(self._taxes) + '</IVA>' + \
						'<MntTotal>' + str(self.total_amount) + '</MntTotal>' + \
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
		return '<FchEmis>' + str(datetime.datetime.now()) + '</FchEmis>'

	def dump_payment_method(self):
		return '<FmaPago>' + str(self._dte_payment_method) + '</FmaPago>'

	def dump_expiry_date(self):
		return '<FchVenc>' + str(self._dte_expiry_date) + '</FchVenc>'


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

	def get_item_list_for_template(self):
		return self._items

	def get_first_item_description(self):
		return self._items[1]['Description']

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
	def __init__(self):
		print("Not implemented")

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
		dumped = dumped + '<FRMA algoritmo="SHA1withRSA">' + self._parameters['_EmbeddedSignature'] + '</FRMA>'
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
		for elem in tree.iter():
			property = self.get_property_by_markup(elem.tag)
			if property is not None:
				self._parameters[property] = elem.text

		self.embedded_private_key = self._parameters['_RSAPrivateKey']

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
	_timestamp = datetime.datetime.now()
	_caf = None
	_document_id = ''
	_ted = ''

	def __init__(self, header, items, discount, reference, other, signature, timestamp, caf=None, signer=None):
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

	def generate_ted(self):
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
				  '<TSTED>' + str(datetime.datetime.now()) + '</TSTED>' + \
				  '</DD>'

		signature = self.sign(document_data, self._caf.embedded_private_key)
		ted = '<TED version="1.0">' + \
			document_data + \
		  '<FRMT algoritmo="SHA1withRSA">' + signature + '</FRMT>' + \
		  '</TED>'
		return ted

	def sign(self, data, key, algorithm='SHA1withRSA'):
		if self._signer is not None:
			self._signer.key = key
			sign = self._signer.sign_with_algorithm(data, algorithm)
			return sign
		else:
			import xmlsec
			import base64
			print(str(key))
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
		return '<Documento ID="' + self._document_id + '">' + self._header.dump() + self._items.dump() + self.generate_ted() + '</Documento>'

	def to_template_parameters(self):
		dict = { 'Sender': {
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
				'Comment': self._header.comment
		}

		return dict

class DTEBuidler:
	def build(self, type, sender, receiver, header, items, caf):
			sender_object = DTEPerson(1, sender)
			receiver_object = DTEPerson(0, receiver)
			header_object = DTEHeader(sender_object, receiver_object, type, 1, 1, datetime.datetime.now(), header)

			""" Items """
			items_object = DTEItems(type, items)

			if isinstance(caf, DTECAF):
				caf_object = caf
			else:
				caf_object = DTECAF(parameters=caf, signature=signature, private_key=private_key)
				signature = caf['_Signature']
				private_key = caf['_PrivateKey']

			dte = DTE(header_object, items_object, '', '', '', '', '',caf=caf_object)

			dte_etree = etree.fromstring(dte.dump())
			pretty_dte = etree.tostring(dte_etree, pretty_print=True).decode('UTF-8')
			return dte_etree, pretty_dte, dte

if __name__ == "__main__":
	""" Dump test XML """
	EXPEDITION_DOCUMENT_TYPE = 52
	sender_parameters = {'RUT':'XXXXXXX-3',
						'Name':'Matthieu AMOROS',
						'Activity':'PERSONA',
						'Address':'1606 Pasaje X',
						'Comune':'Teno',
						'City':'Curico',
						'Acteco': '1234'}
	sender = DTEPerson(1, sender_parameters)

	receiver_parameters = {'RUT':'XXXXXXX-4',
						'Name':'Matthieu AMOROS',
						'Activity':'PERSONA',
						'Address':'555 Pasaje X',
						'Comune':'Las condes',
						'City':'Santiago'}
	receiver = DTEPerson(0, receiver_parameters)

	""" Header """
	specific_parameters = {'ExpeditionType': '1', #Paid by sender
							'MovementType': '2' #Internal
							}

	header = DTEHeader(sender, receiver, EXPEDITION_DOCUMENT_TYPE, 1, 1, datetime.datetime.now(), specific_parameters)

	""" Items """

	item_list = {1: {'CodeType':'INT01',
						'Code':'18KGMZ',
						'Extension':'1',
						'Name':'CAJA MANZANA 18KG',
						'Description':'CAJA MANZANA FRESCA 18KG GALA',
						'Quantity':'20',
						'Unit':'UN',
						'UnitPrice':'1000',
						'ItemPrice':'20000'
						},
				2: {'CodeType':'INT01',
									'Code':'10KGPE',
									'Extension':'1',
									'Name':'CAJA PERA 10KG',
									'Description':'CAJA PERA FRESCA 10KG ABATE',
									'Quantity':'20',
									'Unit':'UN',
									'UnitPrice':'500',
									'ItemPrice':'10000'
									},
				3: {'CodeType':'INT01',
									'Code':'PAL1',
									'Extension':'1',
									'Name':'PALLET 100x120',
									'Description':'PALLET MADERA DE 100x120CM',
									'Quantity':'2',
									'Unit':'UN',
									'UnitPrice':'10',
									'ItemPrice':'20'
									}
				}

	items = DTEItems(EXPEDITION_DOCUMENT_TYPE, item_list)

	caf = DTECAF(parameters={}, signature='', private_key='')

	""" Could be loaded from XML too """
	caf.load_from_XML('../../cert/caf_test.xml')
	dte = DTE(header, items, '', '', '', '', '',caf=caf)

	dte_etree = etree.fromstring(dte.dump())
	pretty_dte = etree.tostring(dte_etree, pretty_print=True).decode('UTF-8')
	print(pretty_dte)
