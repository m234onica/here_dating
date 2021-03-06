var base_url = config.BASE_URL;
var app_id = config.APP_ID;

function pair_status(status) {
    var timeout = config.SET_TIMEOUT;

    if (status == "pairing") {
        $("#pairing-status").css("display", "");
        window.setTimeout(close_Webview, timeout);
    } else if (status == "paired") {
        $("#paired-status").css("display", "");
        window.setTimeout(close_Webview, timeout);
    } else {
        $("#pair-form").css("display", "");
    }
}

$("input#placeId")
    .on("keyup", function () {
        var placeId = $("#placeId").val().trim();

        $(".error").remove();
        $(".invalid-feedback").remove();

        if (placeId.length != 4) {
            $("#placeId").addClass("is-invalid")
                .after("<div class='error invalid-feedback'>沒有這個地標編號，請再確認一次</div>");
            $("#pair-submit").attr("disabled", true);

        } else {
            $.get(
                base_url + "/api/place/" + placeId,
                function (data, status) {

                    if (status == "success") {
                        if (data.payload == true) {
                            $(".error").remove();
                            $("#placeId").removeClass('is-invalid').addClass('is-valid')
                            $("#pair-submit").attr("disabled", false);
                        } else {
                            $("#placeId").addClass("is-invalid")
                                .after("<div class='error invalid-feedback'>沒有這個地標編號，請再確認一次</div>");
                            $("#pair-submit").attr("disabled", true);
                        }
                    }
                }
            )
        }
    }).on("keyup", function () {
        $(".error").remove();
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


function message_status(userId, pairId) {
    var timeout = config.SET_TIMEOUT;
    var status = get_status(userId).status;
    var current_pairId = get_status(userId).pairId;
    var placeName = get_place_name(userId);

    if (status == "noPair") {
        $("#sended").css("display", "");
        document.getElementById("send-placeName").innerHTML = placeName;
        window.setTimeout(close_Webview, timeout);

    } else if (current_pairId != pairId || status != "unSend") {
        $("#leave-pair").css("display", "");
        document.getElementById("leave-placeName").innerHTML = placeName;
        window.setTimeout(close_Webview, timeout);

    } else {
        $("#message-form").css("display", "");
    }
}

function get_place_name(userId) {
    var placeName = null;

    $.ajax({
        type: "GET",
        url: base_url + "/api/" + userId + "/placeName",
        async: false,
        success: function (data) {
            placeName = data.placeName
        }
    })
    return placeName;
}


$("#lastWord").on("keyup", function () {
    $(".error").remove();
    $("#lastWord").removeClass("is-invalid");
})

$("#message-submit").on("click", function (e) {
    e.preventDefault()

    MessengerExtensions.getContext(
        app_id,
        function success(uids) {
            var userId = uids.psid;
            var data = {
                "lastWord": $("#lastWord").val(),
                "contact": $("#contact").val(),
                "userId": userId,
            }

            if (data["lastWord"].trim() == "") {
                $("#lastWord").addClass("is-invalid").after("<div class='error invalid-feedback'>此為必填選項</div>");

            } else {
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
            }
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