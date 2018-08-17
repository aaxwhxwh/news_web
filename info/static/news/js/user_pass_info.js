function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pass_info").submit(function (e) {
        e.preventDefault();
        $('.error_tip').hide();

        // TODO 修改密码
        var old_passwd = $('#old_passwd').val();
        var new_passwd = $('#new_passwd').val();
        var check_new_passwd = $('#check_new_passwd').val();
        console.log(old_passwd,new_passwd,check_new_passwd)

        if (!old_passwd){
            $('.error_tip').show();
            return
        }

        if(!new_passwd || !check_new_passwd){
            $('.error_tip').show();
            return
        }

        if(new_passwd != check_new_passwd){
            $('.error_tip').html('两次密码不一致，请重新输入');
            $('.error_tip').show();
            return
        }
        if (new_passwd.length < 6) {
            $('.error_tip').html("密码长度不能少于6位");
            $('.error_tip').show();
            return;
        }
        var params = {
            "old_passwd": old_passwd,
            "new_passwd": new_passwd,
            "check_new_passwd": check_new_passwd
        };
        $.ajax({
            url: '/user/user_pass_info.html',
            type: 'post',
            data: JSON.stringify(params),
            headers: {
              "X-CSRFToken": getCookie('csrf_token')
            },
            contentType: 'application/json',
            dataType: 'json',
            success: function (resp) {
                if(resp.errno == '0'){
                    alert(resp.errmsg)
                    window.location.reload()
                }else {
                    alert(resp.errmsg)
                }
            }
        })
    })
});