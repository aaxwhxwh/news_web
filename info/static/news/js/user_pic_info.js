function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pic_info").submit(function (e) {
        e.preventDefault();

        var data = new FormData();
        data.append('file', $('#user_pic')[0].files[0]);
        if(!data){
            return
        }else {
            //TODO 上传头像
            $.ajax({
                url: '/user/user_pic_info.html',
                type: 'post',
                data: data,
                headers: {
                    "X-CSRFToken": getCookie("csrf_token")
                },
                cache: false,
                processData: false,
                contentType: false,
                success: function (resp) {
                    if(resp.errno == '0'){
                        top.location.reload()
                    }else{
                        alert()
                    }
                }
            })
        }
    })
});