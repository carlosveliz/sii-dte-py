import datetime

class DTEHeader:
	""" Document identity, composed of sender, reciber information, document type, and total amount """
	_sender = None
	_receiver = None
	_dte_document_type = 0
	_total_amount = 0

	def dump(self):
		return '<DTEHeader></DTEHeader>'

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
	_header = DTEHeader()
	_items = DTEItems()
	_discount = ''
	_reference = [] #DTEReference
	_other_charges = [] #DTEItems()
	_sii_signature = None
	_timestamp = datetime.datetime.now()
