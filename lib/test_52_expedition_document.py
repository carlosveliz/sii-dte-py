import datetime
from lxml import etree
from models.dte import DTEBuidler

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

	receiver_parameters = {'RUT':'XXXXXXX-4',
						'Name':'Matthieu AMOROS',
						'Activity':'PERSONA',
						'Address':'555 Pasaje X',
						'Comune':'Las condes',
						'City':'Santiago'}
	""" Header """
	specific_header_parameters = {'ExpeditionType': '1', #Paid by sender
							'MovementType': '2' #Internal
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

	caf_parameters = {'RUT':'XXXXXXX-3',
						'Name':'Matthieu AMOROS',
						'Type':'52',
						'From':'0',
						'To':'10',
						'FechaAuthorization':'2020-03-17',
						'RSAPrivateKeyModule':'waVWjYCJLcFAtrWgXheAxkGF2sdfsdfsdf1gTQ3OenDOCezdztNKtLU8hczwWNH/iPA3jwqVGjPt6kYOqz1212d5uIAN6sW8tKQgU8IEfgIw==',
						'RSAPrivateKeyExp':'Aw=l',
						'KeyId':'300',
						'Signature': 'E/waVWjYCJLcFAtrWgXheAxkGF2sdfsdfsdf1gTQ3OenDOCezdztNKtLU8hczwWNH+5fyH4JbHdO24JRHyLNsw==',
						'PrivateKey': 'sdfasdfASDAsd#$3423'
						}
	builder = DTEBuidler()

	dte_etree, pretty_dte = builder.build(EXPEDITION_DOCUMENT_TYPE, sender_parameters, receiver_parameters, specific_header_parameters, item_list, caf_parameters)
	print(pretty_dte)
else:
	print("Test only")
