var captcha_done = false;
var requests_available = false;

function recaptchaDone() {
  captcha_done = true;
  updateSubmitButton();
}

function recaptchaExpired() {
  captcha_done = false;
  updateSubmitButton();
}

function updateSubmitButton() {
  if (captcha_done && requests_available) {
    $("#submit-button").removeAttr("disabled");
  } else {
    $("#submit-button").attr("disabled", "true")
  }
}

$(document).ready(function() {
  function updateAvailableRequests() {
    $.post("rate", function(data, status, res) {
      $("#available-requests").text(data.available_requests);
      if (data.available_requests < 1) {
        requests_available = false;
        $("#next-available-request").text("Seuraava yritys aukeaa " + moment.unix(data.next_available_request).format("HH:mm") + ".");
      } else {
        requests_available = true;
        $("#next-available-request").text("");
      }

      updateSubmitButton();

      $("#max-requests").text(data.max_requests);
      $("#time").text(data.time/60);

      $("#correct-counter").text(data.correct_counter + " ✓");
      $("#incorrect-counter").text(data.incorrect_counter + " ✗");
    });
  }

  updateAvailableRequests();
  setInterval(updateAvailableRequests, 1000*60);

  $("#form").submit(function(event) {
    event.preventDefault();

    $.post("check", $(this).serializeArray(), function(data, status, res) {
      grecaptcha.reset();
      captcha_done = false;
      updateSubmitButton();
      updateAvailableRequests();
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
        $("#status").html("<span class=\"error\">Muista suorittaa reCAPTCHA!</span>");
      }
    });
  });
});
