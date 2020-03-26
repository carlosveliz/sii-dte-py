# sii-dte-py
Web App used to send Chilean SII DTE documents

# Current state
/_!_\ This software has yet to pass SII certification /_!_\
Its current state allows you to :
	-	Generate PDF with correct format for document type 52
	- Get a token from SII
	- Parse CAF document
	- Convert your PFX file to SII expected format using OpenSSL

# Install
```
pip3 install -r requirements.txt
```
# Use cases
 - Basic Web UI :
	 ```
		python3 run.py
	 ```
	 	-	First "login" with your RUT (this is just a mean to initiate session, no authentication)
	 	-	Then load your certiciate and password
		- Finally call "/token" to see your token

 - get_token <pfx_file_path> <pfx_password>
 		```
		python3 run.py get_token '/home/user/Desktop/cert/my-cert.pfx' Password
		* Application secret key : X
		getSeed
		Seed : 024945556814
		writing RSA key
		getToken
		Token : AF6X9CCA6F9Z9
		```
 - generate_cert <pfx_file_path> <pfx_password>
		```
		python3 run.py generate_cert '/home/user/Desktop/cert/my-cert.pfx' Password
		* Application secret key : X
		writing RSA key
		No output
		```
 - generate_pdf <sii type>
		```
		 	python3 run.py generate_pdf 52

		 * Application secret key : X
		Loading CAF from xml
		QStandardPaths: XDG_RUNTIME_DIR not set, defaulting to '/tmp/runtime-root'
		libpng warning: iCCP: known incorrect sRGB profile
		libpng warning: iCCP: known incorrect sRGB profile
		Loading page (1/2)
		Printing pages (2/2)                                               
		Done       
		Output in temp directory
		```
