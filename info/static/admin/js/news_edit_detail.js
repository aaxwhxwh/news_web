function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function(){
    $(".news_edit").submit(function (e) {
        e.preventDefault()
        // TODO 新闻编辑提交
        var news_id = $('.input_txt2').attr('news_id')
        var data = new FormData($('.form-group'))
        console.log(data)
        $.ajax({
            url: '/admin/news_edit_detail/'+news_id,
            type: 'post',
            data: data,
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            cache: false,
            processData: false,
            contentType: false,
            success: function (resp) {
                if (resp.errno == '0'){
                    window.location.href = '/admin/news_edit'
                }
            }
        })
    })
})

// 点击取消，返回上一页
function cancel() {
    history.go(-1)
}