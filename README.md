# sii-dte-py
Web App used to send Chilean SII DTE documents

## Current state
<aside class="notice">
This software **has yet to pass SII certification**, it's currently in developpment.
Its main goal is to understand how SII works and how to communicate with it in a clear way.
The project is currently published under **MIT License** so feel free to copy, modify, and contribute.
</aside>

Current state allows you to :
	-	Generate PDF with correct format for document type 52
	- Generate PDF from DTE XML (documenty type 52 only)
	- Get a token from SII
	- Parse CAF document
	- Convert your PFX file to SII expected format using OpenSSL

## Install
```
pip3 install -r requirements.txt
```
## Use cases
 - Basic Web UI (Flask):
	 ```
	python3 run.py
	 ```
	 	-	First "login" with your RUT (this is just a mean to initiate session, no authentication)
	 	-	Then load your certiciate and password
		-   Finally call "/token" to see your token

 - get_token <pfx_file_path> <pfx_password>
 		```
		python3 run.py get_token '/home/user/Desktop/cert/my-cert.pfx' Password
		```
		Result
		```
		Seed : 024945556814
		Token : AF6X9CCA6F9Z9
		```
 - generate_cert <pfx_file_path> <pfx_password>
		```
		python3 run.py generate_cert '/home/user/Desktop/cert/my-cert.pfx' Password
		```
		Result
		```
		No output, key loaded in memory (useless at this stage...)
		```
 - generate_pdf <sii type>
		```
		 	python3 run.py generate_pdf 52
 		```
		Result
		```
		PDF file output in temp directory
		```
	- generate_pdf_from_xml <xml_file_path>
 		```
 		python3 run.py generate_pdf_from_xml '/home/user/Desktop/xml/xml-52.pfx'
 		```
 		Result
 		```
 		PDF file output in temp directory
 		```
## Use cases
A PDF sample generated using this project is available at "documents/sample_52.pdf"
