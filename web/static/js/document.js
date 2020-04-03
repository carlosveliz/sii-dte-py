function saveDocument(documentDivId) {
	let parameters = $('#' + documentDivId).find('input, select, textarea').serializeArray();
	console.log(parameters);
}
