function saveDocument(documentDivId) {
	let parameters = $('#' + documentDivId).find('input, select, textarea').serializeArray();
	let correctFormat = buildCompatibleJsonModel(parameters);
	$.ajax({
		type: 'POST',
		/**/
		url: '/dte',
		/**/
		dataType: 'application/json',
		data: JSON.stringify(correctFormat),
		success: function () {

		},
		error: function (ex) {
		}
	});
}

function buildCompatibleJsonModel(parameters) {
	let correctFormat = {};

	for (param in parameters) {
		let item = parameters[param];
		if(item.name.indexOf('-') > 0)
		{
			setItemByPath(item.value, item.name, correctFormat);
		}
		else {
			correctFormat[item.name] = item.value;
		}
	}

	return correctFormat;
}

//Unflatten items
function setItemByPath(value, path, array)
{
	let pathNode = path.split('-');
	let node = path.split('-')[0];
	if(pathNode.length == 1)
	{
		//End of path
		array[node] = value;
	}
	else
	{
		if(!(node in array))
		{
			array[node] = {};
		}
		//Remove node and pass path
		setItemByPath(value, path.replace(node + '-', ''), array[node]);
	}
}

function addNewDetailRow() {
	//Get row count
	let rowCount = $("#detailTable > tbody > tr ").length;

	//Get target
	let target = $("#detailTable > tbody > .newRow");
	let newRow = '<tr class="newRow">' + target.html() + '</tr>';
	let elements = $("#detailTable > tbody > .newRow > td > input");

	//Update inputs name with unique id
	elements.each(function(element) {
		let elem = $(elements[element]);

		if(elem.attr('name') != undefined)
		{
			let newName = 'Details-' + rowCount + '-' + elem.attr('name').split('-')[2];
			elem.attr('name', newName);
		}

		if(!elem.hasClass("remove"))
			elem.addClass('disabled');
		else {
			elem.attr("disabled", false);
			}
	});

target.removeClass("newRow");
target.after(newRow);
}

function removeNewDetailRow(target) {
	parent = target.closest("tr");
	parent.remove();
}
