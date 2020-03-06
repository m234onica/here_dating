$('input#placeId')
    .on('keyup', function () {
        var placeId = $('#placeId').val().trim();
        if (placeId.length == 4) {
            $.ajax({
                type: "GET",
                url: base_url + "/api/place/" + placeId,
                dataType: 'json',
                contentType: 'application/json; charset=utf-8',
                success: function(data) {
                    console.log(data.placeId);
                },
                error: function(data) {
                    console.log(data.status);
                    
                }
            })
        }
    })

$('#intro-submit').on('click', function (e) {
    e.preventDefault()
    MessengerExtensions.getContext(
        app_id,
        function success(uids) {
            var psid = uids.psid;
            var data = {
                'placeId': $('#placeId').val(),
                'userId': psid,
            }
            $.ajax({
                type: "POST",
                url: base_url + "/api/user/pair",
                dataType: 'json',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify(data),
            }).always(function (d) {
                console.log(d);
                if (d.payload == "pairing") {
                    window.location.href = base_url + '/wait';
                } else {
                    close_Webview();
                }
            })
        },
        function error(err, errorMessage) {
            alert(JSON.stringify(errorMessage));
        });
})

function close_Webview() {
    MessengerExtensions.requestCloseBrowser(
        function success() {
            // webview closed
            console.log('success');
        }, function error(err) {
            // an error occurred
            console.log(err);
        });
}