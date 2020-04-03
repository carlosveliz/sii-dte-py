function saveDocument(documentDivId) {
	let parameters = $('#' + documentDivId).find('input, select, textarea').serializeArray();
	console.log(parameters);
}

function addNewDetailRow() {
	//Get row count
	let rowCount = $("#detailTable > tbody > tr ").length;

	//Get target
	let target = $("#detailTable > tbody > .newRow");
	let newRow = '<tr class="newRow">' + target.html() + '</tr>';
	let elements = $("#detailTable > tbody > .newRow > td > input");
	target.removeClass("newRow");

	//Update inputs name with unique id
	elements.each(function(element) {
			let elem = $(elements[element]);
			elem.attr('name', rowCount + '-' + elem.attr('name'));
			if(!elem.hasClass("remove"))
				elem.attr('disabled', true);
			else {
				elem.attr('disabled', false);
			}
		}
	);

	target.after(newRow);
}

function removeNewDetailRow(target) {
	parent = target.closest("tr");
	parent.remove();
}
