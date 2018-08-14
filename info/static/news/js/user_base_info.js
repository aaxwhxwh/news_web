function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {

    $(".base_info").submit(function (e) {
        e.preventDefault()

        var signature = $("#signature").val()
        var nick_name = $("#nick_name").val()
        var gender = $(".gender").val()

        if (!nick_name) {
            alert('请输入昵称')
            return
        }
        if (!gender) {
            alert('请选择性别')
        }

        // TODO 修改用户信息接口
        var params = {
            "nick_name": nick_name,
            "gender": gender,
            "signature": signature
        };
        $.ajax({
            url: "/user_base_info.html",
            type: 'post',
            data: JSON.stringify(params),
            headers: {
              "X-CSRFToken": getCookie("csrf-token")
            },
            contentType: 'application/json',
            dataType: 'json',
            success: function (resp) {
                if(resp.errno == '0') {
                    top.location.reload()
                }
            }
        })
    })
});