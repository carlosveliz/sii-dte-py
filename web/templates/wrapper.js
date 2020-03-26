function getToken() {
	$.ajax({
						url: '/token',
						type: 'GET',
						dataType: 'json',
						success: function(data) {
							console.log(data);
					}
	});
}

function generatePDF() {
	$.ajax({
						url: '/certificate',
						type: 'POST',
						dataType: 'json',
						data: $('form').serialize(),
						success: function(data) {
					}
	});
}

function  getPreview() {
	$.ajax({
						url: '/certificate',
						type: 'POST',
						dataType: 'json',
						data: $('form').serialize(),
						success: function(data) {
					}
	});
}

function login() {
	$.ajax({
						url: '/login',
						type: 'POST',
						dataType: 'json',
						data: $('form').serialize(),
						success: function(data) {
					}
	});
}
