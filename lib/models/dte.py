import datetime

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
	_sender = DTEPerson(1, None)
	_receiver = DTEPerson(0, None)
	_dte_document_type = 0
	_dte_document_number = 0
	_dte_export_type = 0
	_dte_export_indicator = 0
	_dte_payment_method = 0
	_dte_expiry_date = 0
	_net_amount = 0
	_tax_rate = 0
	_taxes = 0
	_total_amount = 0

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

	def __init__(self, sender, receiver, document_type, document_number, payment_method, expiry_date, specific_parameters):
		""" specific_parameters parameter should contains document type based parameters """
		assert(document_type in self.__valid_document_types)
		self._sender = sender
		self._receiver = receiver
		self._dte_document_type = document_type
		self._dte_document_number = document_number
		self._dte_payment_method = payment_method
		self._dte_expiry_date = expiry_date
		self._specifics = specific_parameters

	def dump_specifics(self):
		dumped = ''
		for param in self._specifics:
			markup = self.__specifics_by_document_type[self._dte_document_type][param]
			value = self._specifics[param]
			dumped = dumped + '<' + markup + '>' + str(value) + '</' + markup + '>'

		return dumped

	def dump(self):
		return '<Encabezado>' + self.dump_document_identification() + \
		self._sender.dump()  + \
		self._receiver.dump() + \
		self.dump_totales() + \
		 '</Encabezado>'

	def dump_totales(self):
		return '<Totales>' + '<MntNeto>' + str(self._net_amount) + '</MntNeto>' + \
						'<TasaIVA>' + str(self._tax_rate) + '</TasaIVA>' + \
						'<IVA>' + str(self._taxes) + '</IVA>' + \
						'<MntTotal>' + str(self._total_amount) + '</MntTotal>' + \
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
		return '<Folio>'+ str(self._dte_document_number) +'</Folio>'

	def dump_document_type(self):
		return '<TipoDTE>' + str(self._dte_document_type) + '</TipoDTE>'

	def dump_issue_date(self):
		return '<FchEmis>' + str(datetime.datetime.now()) + '</FchEmis>'

	def dump_payment_method(self):
		return '<FmaPago>' + str(self._dte_payment_method) + '</FmaPago>'

	def dump_expiry_date(self):
		return '<FchVenc>' + str(self._dte_expiry_date) + '</FchVenc>'

class DTEItems:
	_items = []

	def add_item(self, item):
		_items.append(item)

	def dump(self):
		return '<DTEItems></DTEItems>'

class DTEItem:
	_code = ''
	_quantity = 0
	_net_value = 0
	_raw_value = 0
	_discount = 0
	_additional_amount = 0
	_document_reference = 0

	def dump(self):
		return '<DTEItem></DTEItem>'

class DTEReference:
	_code = ''
	_dte_document_type = 0

	def dump(self):
		return '<DTEReference></DTEReference>'

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

	def __init__(self, header, items, discount, reference, other, signature, timestamp):
		self._header = header
		self._items = items
		self._discount = discount
		self._reference = reference
		self._other_charges = other
		self._sii_signature = signature
		self._timestamp = timestamp

if __name__ == "__main__":
	""" Dump test XML """
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

	header = DTEHeader(sender, receiver, 52, 1, 1, datetime.datetime.now(), specific_parameters)
	print(header.dump())
