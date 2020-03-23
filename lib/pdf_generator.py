
"""

 Generate PDFs

 Needed : sudo apt install -y wkhtmltopdf

"""

import pdfkit
import pdf417
from models.dte import DTE, DTEBuidler, DTECAF
from jinja2 import Environment, FileSystemLoader

class PDFGenerator:

	__template_by_type = {
							52:'web/templates/sii_document_52.html',
							33:'web/templates/sii_document_33.html'
						}

	def generate(self, dte):
		# Use False instead of output path to save pdf to a variable
		ted = self._generate_png_ted(dte.generate_ted())
		html = self._populate_jinja_template(dte, ted)
		options = {
			'page-size': 'A3',
			'dpi': 600
        }
		pdf = pdfkit.from_string(html, '../temp/test.pdf', options=options)
		return ''

	def _populate_jinja_template(self, dte, ted):
		""" Get template path by type """
		template_path = self.__template_by_type[52]
		with open(template_path) as f:
			template_str = f.read()
		""" Load template """
		template = Environment(loader=FileSystemLoader(['/web/templates', '../temp'])).from_string(template_str)
		""" Get template parameters """
		template_parameters = dte.to_template_parameters()
		""" Render """
		html_str = template.render(parameters=template_parameters, ted=ted)
		return html_str

	def _generate_svg_ted(self, ted_string):
		codes = pdf417.encode(ted_string, security_level=5)
		svg = pdf417.render_svg(codes, scale=3, ratio=3)  # ElementTree object
		return svg

	def generate_test_svg_ted(self, ted_string, filepath='../temp/test.svg'):
		unique = 1
		filename = str(unique) + 'barcode.svg'
		filepath = '/home/sunpaz/DTE/sii-dte-py/temp/' + filename
		codes = pdf417.encode(ted_string, security_level=5)
		svg = pdf417.render_svg(codes, scale=3, ratio=3)  # ElementTree object
		svg.write(filepath)
		return filename

	def _generate_png_ted(self, ted_string):
		unique = 1
		filename = str(unique) + 'barcode.png'
		filepath = '/home/sunpaz/DTE/sii-dte-py/temp/' + filename
		codes = pdf417.encode(ted_string, columns=10, security_level=5)
		image = pdf417.render_image(codes, scale=3, ratio=3, padding=5)  # Pillow Image object
		image.save(filepath)
		return filepath


if __name__ == "__main__":
	pdf = PDFGenerator()
	""" Dump test XML """
	EXPEDITION_DOCUMENT_TYPE = 52
	sender_parameters = {'RUT':'XXXXXXX-3',
						'Name':'Matthieu AMOROS',
						'Activity':'PERSONA',
						'Address':'1606 Pasaje X',
						'Comune':'Teno',
						'City':'Curico',
						'Acteco': '1234'}

	receiver_parameters = {'RUT':'XXXXXXX-4',
						'Name':'Matthieu AMOROS',
						'Activity':'PERSONA',
						'Address':'555 Pasaje X',
						'Comune':'Las condes',
						'City':'Santiago'}
	""" Header """
	specific_header_parameters = {'ExpeditionType': '1', #Paid by sender
							'MovementType': '2', #Internal
							'Comment' : "TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST"
							}

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

	caf = DTECAF(parameters={}, signature='', private_key='')
	caf.load_from_XML('../cert/caf_test.xml')

	builder = DTEBuidler()

	_, pretty_dte, dte_object = builder.build(EXPEDITION_DOCUMENT_TYPE, sender_parameters, receiver_parameters, specific_header_parameters, item_list, caf)
	pdf.generate(dte_object)

	myXML = open('../temp/DTE_52.xml', "w")
	myXML.write(pretty_dte)
