$("input#placeId")
    .on("keyup", function () {
        var placeId = $("#placeId").val().trim();

        $(".placeId_error").remove();
        $(".invalid-feedback").remove();

        if (placeId.length == 4) {
            $.ajax({
                type: "GET",
                url: base_url + "/api/place/" + placeId,
                dataType: "json",
                contentType: "application/json; charset=utf-8",
                success: function (data) {
                    $(".placeId_error").remove();
                    $("#intro-submit").attr("disabled", false);
                },
                error: function (data) {
                    $("#placeId").addClass("is-invalid")
                        .after("<div class='placeId_error invalid-feedback'>該店號不存在</div>");
                    $("#intro-submit").attr("disabled", true);

                }
            })
        }
    }).on("keyup", function () {
        $(".placeId_error").remove();
        $("#placeId").removeClass("is-invalid").removeClass("is-valid")
    })

$("#intro-submit").on("click", function (e) {
    e.preventDefault()

    MessengerExtensions.getContext(
        app_id,
        function success(uids) {
            var psid = uids.psid;
            var data = {
                "placeId": $("#placeId").val(),
                "userId": psid,
            }
            $.ajax({
                type: "POST",
                url: base_url + "/api/user/pair",
                dataType: "json",
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify(data),
            }).always(function (d) {
                console.log(d);
                if (d.payload == "pairing") {
                    window.location.href = base_url + "/wait";
                } else {
                    close_Webview();
                }
            })
        },
        function error(err, errorMessage) {
            alert(JSON.stringify(errorMessage));
        });
})

function get_status() {
    MessengerExtensions.getContext(
        app_id,
        function success(uids) {
            var psid = uids.psid;

            $.ajax({
                type: "GET",
                url: base_url + "/api/user/status/" + psid,
                dataType: "json",
                contentType: "application/json; charset=utf-8",

                success: function (data) {
                    if (data.payload == "pairing") {
                        window.location.href = base_url + "/wait";
                    } else {
                        close_Webview();
                    }
                },
                error: function (err) {
                    window.location.href = base_url + "/leave";
                }
            })
        }
    )
}

function close_Webview() {
    MessengerExtensions.requestCloseBrowser(
        function success() {
            // webview closed
            console.log("success");
        }, function error(err) {
            // an error occurred
            console.log(err);
        });
}