
"""

 Generate PDFs

 Needed : sudo apt install -y wkhtmltopdf

"""

import pdfkit
import pdf417
import os
from lib.models.dte import DTE, DTEBuidler, DTECAF
from jinja2 import Environment, FileSystemLoader

FILE_DIR = os.path.dirname(os.path.realpath(__file__))

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
		pdf = pdfkit.from_string(html, FILE_DIR + '/../temp/test.pdf', options=options)
		return ''

	def _populate_jinja_template(self, dte, ted):
		""" Get template path by type """
		template_path = self.__template_by_type[52]
		with open(template_path) as f:
			template_str = f.read()
		""" Load template """
		template = Environment(loader=FileSystemLoader([FILE_DIR + '/web/templates', FILE_DIR + '/../temp'])).from_string(template_str)
		""" Get template parameters """
		template_parameters = dte.to_template_parameters()
		""" Render """
		html_str = template.render(parameters=template_parameters, ted=ted)
		return html_str

	def _generate_svg_ted(self, ted_string):
		codes = pdf417.encode(ted_string, security_level=5)
		svg = pdf417.render_svg(codes, scale=3, ratio=3)  # ElementTree object
		return svg

	def generate_test_svg_ted(self, ted_string, filepath=FILE_DIR + '/../temp/test.svg'):
		unique = 1
		filename = str(unique) + 'barcode.svg'
		filepath = FILE_DIR + '/../temp/' + filename
		codes = pdf417.encode(ted_string, security_level=5)
		svg = pdf417.render_svg(codes, scale=3, ratio=3)  # ElementTree object
		svg.write(filepath)
		return filename

	def _generate_png_ted(self, ted_string):
		unique = 1
		filename = str(unique) + 'barcode.png'
		filepath = FILE_DIR + '/../temp/' + filename
		codes = pdf417.encode(ted_string, columns=10, security_level=5)
		image = pdf417.render_image(codes, scale=3, ratio=3, padding=5)  # Pillow Image object
		image.save(filepath)
		return filepath
