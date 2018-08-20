function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {

    $(".focused").click(function () {
        // TODO 取消关注当前新闻作者
        var followed_id = $('.author_card').attr('user_id')
                var action = 'cancel_focus'
        var params = {
            "author_id": followed_id,
            "action": action
        }
        $.ajax({
            url: '/user/user_follow.html',
            type: 'post',
            data: JSON.stringify(params),
            headers: {
                "X-CSRFToken": getCookie('csrf_token')
            },
            contentType: 'application/json',
            success: function (resp) {
                if (resp.errno == '0'){
                    location.reload()
                }else{
                    alert(resp.errmsg)
                }
            }
        })
    })
})