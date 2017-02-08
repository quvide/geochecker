$(document).ready(function() {
	$("#form").submit(function(event) {
	  event.preventDefault();

		$.post("#", $(this).serializeArray(), function(data, status, res) {
			for (var attr in data.fields) {
				$("#" + attr).removeClass();
				$("#" + attr).addClass(data.fields[attr]);
			}

			if (data.coordinates) {
				$("#coordinates").html("<p class=\"monospace\">" + data.coordinates + "</p>");
			}
		});
	});
});
