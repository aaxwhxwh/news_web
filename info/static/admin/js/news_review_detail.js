function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function(){
    $(".news_review").submit(function (e) {
        e.preventDefault()
        var news_id = $('#news_id').attr('value')
        var action = $('input:radio:checked').val()
        var reason = $('.input_multxt').val()

        var params = {
            'news_id': news_id,
            'action': action,
            'reason': reason
        }

        $.ajax({
            url: '/admin/news_review_detail/' + news_id,
            type: 'post',
            data: JSON.stringify(params),
            headers: {
                "X-CSRFToken": getCookie('csrf_token')
            },
            contentType: 'application/json',
            success: function (resp) {
                if (resp.errno == '0'){
                    window.location.href = '/admin/news_review'
                }else{
                    alert(resp.errmsg)
                }
            }
        })
        // TODO 新闻审核提交

    })
})

// 点击取消，返回上一页
function cancel() {
    history.go(-1)
}