$(document).ready(function() {
	function update_available_requests() {
		$.post("rate", function(data, status, res) {
			$("#available-requests").text(data.available_requests);
			if (data.available_requests === 0) {
				$("#submit-button").attr("disabled", "true")
			} else {
				$("#submit-button").removeAttr("disabled");
			}

			$("#max-requests").text(data.max_requests);
			$("#time").text(data.time/60);
		});
	}

	update_available_requests();
	setInterval(update_available_requests, "10000");

	$("#form").submit(function(event) {
	  event.preventDefault();

		$.post("check", $(this).serializeArray(), function(data, status, res) {
			grecaptcha.reset();
			update_available_requests();
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
		});
	});
});
