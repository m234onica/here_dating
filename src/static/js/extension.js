var base_url = config.BASE_URL;
var app_id = config.APP_ID;

$("input#placeId")
    .on("keyup", function () {
        var placeId = $("#placeId").val().trim();

        $(".placeId_error").remove();
        $(".invalid-feedback").remove();

        if (placeId.length != 4) {
            $("#placeId").addClass("is-invalid")
                .after("<div class='placeId_error invalid-feedback'>該店號不存在</div>");
            $("#pair-submit").attr("disabled", true);

        } else {
            $.get(
                base_url + "/api/place/" + placeId,
                function (data, status) {

                    if (status == "success") {
                        if (data.payload == true) {
                            $(".placeId_error").remove();
                            $("#placeId").removeClass('is-invalid').addClass('is-valid')
                            $("#pair-submit").attr("disabled", false);
                        } else {
                            $("#placeId").addClass("is-invalid")
                                .after("<div class='placeId_error invalid-feedback'>該店號不存在</div>");
                            $("#pair-submit").attr("disabled", true);
                        }
                    }
                }
            )
        }
    }).on("keyup", function () {
        $(".placeId_error").remove();
        $("#placeId").removeClass("is-invalid").removeClass("is-valid")
    })


$("#pair-submit").on("click", function (e) {
    $(this).attr("disabled", "disabled");
    $(this).html("搜尋中...");
    e.preventDefault()

    MessengerExtensions.getContext(
        app_id,
        function success(uids) {
            var userId = uids.psid;
            var placeId = $("#placeId").val();
            $.post(
                base_url + "/api/pair/" + placeId + "/" + userId,
                function (data, status) {
                    if (status == "success") {
                        close_Webview();
                    } else {
                        console.log(status);
                    }
                })
        },
        function error(err, errorMessage) {
            console.log(JSON.stringify(errorMessage));
        });
})


function message_status(pairId) {
    var timeout = config.SET_TIMEOUT;
    var status = get_status(userId).status;
    var current_pairId = get_status(userId).pairId;
    document.querySelector(".sk-fading-circle").style.display = "none";

    if (status == "noPair") {
        $("#sended").css("display", "");
        window.setTimeout(close_Webview, timeout);

    } else if (current_pairId != pairId || status != "unSend") {
        $("#leave-pair").css("display", "");
        window.setTimeout(close_Webview, timeout);

    } else {
        $("#message-form").css("display", "");
    }
}


$("#message-submit").on("click", function (e) {
    e.preventDefault()

    MessengerExtensions.getContext(
        app_id,
        function success(uids) {
            var userId = uids.psid;
            var data = {
                "lastWord": $("#lastWord").val(),
                "userId": userId,
            }
            $.ajax({
                type: "POST",
                url: base_url + "/api/user/send",
                dataType: "json",
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify(data),
            }).always(function (d) {
                var payload = d.payload
                if (payload.status == "success") {
                    close_Webview()
                } else {
                    alert(JSON.stringify(payload));
                }
            })
        },
        function error(err, errorMessage) {
            alert(JSON.stringify(errorMessage));
        });
})


function get_status(userId) {
    var result = null;

    $.ajax({
        type: "GET",
        url: base_url + "/api/user/status/" + userId,
        async: false,
        success: function (data) {
            var payload = data.payload
            result = {
                "status": payload.status,
                "pairId": payload.pairId
            };
        },
        error: function (data) {
            console.log(data);
        }
    })
    return result;

}


function close_Webview() {
    MessengerExtensions.requestCloseBrowser(
        function success() {
            // webview closed
        }, function error(err) {
            // an error occurred
            console.log(err);
        });
}