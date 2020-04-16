var base_url = config.BASE_URL;
var app_id = config.APP_ID;
console.log(base_url);

$("input#placeId")
    .on("keyup", function () {
        var placeId = $("#placeId").val().trim();

        $(".placeId_error").remove();
        $(".invalid-feedback").remove();

        if (placeId.length != 4) {
            $("#placeId").addClass("is-invalid")
                .after("<div class='placeId_error invalid-feedback'>該店號不存在</div>");
            $("#intro-submit").attr("disabled", true);

        } else {
            $.get(
                base_url + "/api/place/" + placeId,
                function (data, status) {
                    console.log(status);
                    
                    if (status == "success") {
                        if (data.payload == true) {
                            $(".placeId_error").remove();
                            $("#placeId").removeClass('is-invalid').addClass('is-valid')
                            $("#intro-submit").attr("disabled", false);
                        } else {
                            $("#placeId").addClass("is-invalid")
                                .after("<div class='placeId_error invalid-feedback'>該店號不存在</div>");
                            $("#intro-submit").attr("disabled", true);
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
            result = payload.status;            
        },
        error: function (data) {
            console.log(err);
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