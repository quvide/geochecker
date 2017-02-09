$(document).ready(function() {
	$("#form").submit(function(event) {
	  event.preventDefault();

		$.post("#", $(this).serializeArray(), function(data, status, res) {
			grecaptcha.reset();
			if (data.captcha_success) {
				$("#status").html("");
				for (var attr in data.fields) {
					$("#" + attr).removeClass();
					$("#" + attr).addClass(data.fields[attr]);
				}

				if (data.coordinates) {
					$("#status").html("<span class=\"coordinates\">" + data.coordinates + "</span>");
				}
			} else {
				$("#status").html("<span class=\"error\">Muista täyttää CAPTCHA!</span>");
			}

			$("#available-requests").text(data.available_requests);
			if (data.available_requests === 0) {
				$("#submit-button").prop("disabled", "true")
			}
		});
	});
});
