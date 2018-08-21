function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function(){

    // 打开登录框
    $('.comment_form_logout').click(function () {
        $('.login_form_con').show();
    })

    // 收藏
    $(".collection").click(function () {
        var news_id = $('.collection').attr('data-newid')
        var params = {
            'news_id': news_id,
            'action': "collect"
        };
       $.ajax({
           url: '/news/news_collection',
           type: 'post',
           data: JSON.stringify(params),
           headers: {
             "X-CSRFToken": getCookie('csrf_token')
           },
           contentType: 'application/json',
           success: function (resp) {
               if (resp.errno == '0'){
                   $('.collection').hide();
                   $('.collected').show();
               }else if (resp.errno == "4101") {
                   $('.login_form_con').show()
               }else{
                   alert(resp.errmsg)
               }
           }
       })
    })

    // 取消收藏
    $(".collected").click(function () {
        var news_id = $('.collection').attr('data-newid')
        var params = {
            'news_id': news_id,
            'action': "cancel_collect"
        };
       $.ajax({
           url: '/news/news_collection',
           type: 'post',
           data: JSON.stringify(params),
           headers: {
             "X-CSRFToken": getCookie('csrf_token')
           },
           contentType: 'application/json',
           success: function (resp) {
               if (resp.errno == '0'){
                   $('.collection').show();
                   $('.collected').hide();
               }else{
                   alert(resp.errmsg)
               }
           }
       })
     
    })

        // 评论提交
    $(".comment_form").submit(function (e) {
        e.preventDefault();
        var news_id = $('.collection').attr('data-newid')
        var content = $('.comment_input').val()
        if (!content){
            alert('输入内容后再提交评论')
            return
        }
        var params = {
            "news_id": news_id,
            "content": content,
        }
        $.ajax({
            url: '/news/comment',
            type: 'post',
            data: JSON.stringify(params),
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            contentType: 'application/json',
            success: function (resp) {
                if (resp.errno == '0'){
                    var comment = resp.data;
                    var comment_html = '';
                    comment_html += '<div class="comment_list">'
                    comment_html += '<div class="person_pic fl">'
                    if(comment.user.avatar_url){
                        comment_html += '<img src="'+comment.user.avatar_url+'" alt="用户图标">'
                    }else{
                        comment_html += '<img src="../../static/news/images/worm.jpg" alt="用户图标">'
                    }
                    comment_html += '</div>'
                    comment_html += '<div class="user_name fl">'+comment.user.nick_name +'</div>';
                    comment_html += '<div class="comment_text fl">'
                    comment_html += comment.content;
                    comment_html += '</div>'
                    comment_html += '<div class="comment_time fl">'+comment.create_time+'</div>'
                    comment_html += '<a href="javascript:;" class="comment_up fr">赞</a>'
                    comment_html += '<a href="javascript:;" class="comment_reply fr">回复</a>'
                    comment_html += '<from class="reply_form fl">'
                    comment_html += '<textarea  class="reply_input"></textarea>'
                    comment_html += '<input type="submit" name="" value="回复" class="reply_sub fr" comment_id="'+comment.id+'" news_id="'+news_id+'">'
                    comment_html += '<input type="reset" name="" value="取消" class="reply_cancel fr">'
                    comment_html += '</from>'
                    comment_html += '</div>'
                    $('.comment_list_con').prepend(comment_html)
                    $('.comment_sub').blur();
                    $('.comment_input').value("")
                }else{
                    alert(resp.errmsg)
                }
            }
        })

    })

    $('.comment_list_con').delegate('a,input','click',function(){

        var sHandler = $(this).prop('class');

        if(sHandler.indexOf('comment_reply')>=0)
        {
            $(this).next().toggle();
        }

        if(sHandler.indexOf('reply_cancel')>=0)
        {
            $(this).parent().toggle();
        }

        if(sHandler.indexOf('comment_up')>=0)
        {
            var $this = $(this);
            var action = 'add';
            if(sHandler.indexOf('has_comment_up')>=0)
            {
                // 如果当前该评论已经是点赞状态，再次点击会进行到此代码块内，代表要取消点赞
                action = 'remove'
            }
            var comment_id = $(this).attr('data-commentid')
            var data = {
                "comment_id": comment_id,
                "action": action
            }
            $.ajax({
                url: '/news/comment_like',
                type: 'post',
                data: JSON.stringify(data),
                contentType: 'application/json',
                headers: {
                    "X-CSRFToken": getCookie('csrf_token')
                },
                success: function (resp) {
                    if (resp.errno == '0'){
                        var like_count = $this.attr('data-likecount')
                        if (action == 'add'){
                            like_count = parseInt(like_count) + 1;
                            $this.addClass('has_comment_up')
                        }else{
                            like_count = parseInt(like_count) - 1;
                            $this.removeClass('has_comment_up')
                        }
                        $this.attr('data-likecount', like_count)
                        if (like_count == 0){
                            $this.html('赞')
                        }else {
                            $this.html(like_count)
                        }
                    }else if(resp.errno == "4101"){
                        $('.login_form_con').show()
                    }else{
                        alert(resp.errmsg)
                    }
                }
            })

        }



        if(sHandler.indexOf('reply_sub')>=0)
        {
            // alert('回复评论')
            var news_id = $(this).attr('news_id')
            var content = $('.reply_input').val()
            var parent_id = $(this).attr('comment_id')
            if (!content){
                alert('输入内容后再提交评论')
                return
            }
            var params = {
                "news_id": news_id,
                "content": content,
                "parent_id": parent_id
            }
            $.ajax({
                url: '/news/comment',
                type: 'post',
                data: JSON.stringify(params),
                headers: {
                    "X-CSRFToken": getCookie("csrf_token")
                },
                contentType: 'application/json',
                success: function (resp) {
                    if (resp.errno == '0'){
                        var comment = resp.data;
                        var comment_html = '';
                        comment_html += '<div class="comment_list">'
                        comment_html += '<div class="person_pic fl">'
                        if(comment.user.avatar_url){
                            comment_html += '<img src="'+comment.user.avatar_url+'" alt="用户图标">'
                        }else{
                            comment_html += '<img src="../../static/news/images/worm.jpg" alt="用户图标">'
                        }
                        comment_html += '</div>'
                        comment_html += '<div class="user_name fl">'+comment.user.nick_name +'</div>';
                        comment_html += '<div class="comment_text fl">'
                        comment_html += comment.content;
                        comment_html += '</div>'
                        comment_html += '<div class="reply_text_con fl">'
                        comment_html += '<div class="user_name2">'+comment.parent.user.nick_name+'</div>'
                        comment_html += '<div class="reply_text">'
                        comment_html += comment.parent.content
                        comment_html += '</div>'
                        comment_html += '</div>'
                        comment_html += '<div class="comment_time fl">'+comment.create_time+'</div>'
                        comment_html += '<a href="javascript:;" class="comment_up fr">赞</a>'
                        comment_html += '<a href="javascript:;" class="comment_reply fr">回复</a>'
                        comment_html += '<from class="reply_form fl">'
                        comment_html += '<textarea  class="reply_input"></textarea>'
                        comment_html += '<input type="submit" name="" value="回复" class="reply_sub fr" comment_id="'+comment.id+'" news_id="'+news_id+'">'
                        comment_html += '<input type="reset" name="" value="取消" class="reply_cancel fr">'
                        comment_html += '</from>'
                        comment_html += '</div>'
                        $('.comment_list_con').prepend(comment_html)
                        $('.comment_up').show()
                        $('.comment_reply').show()
                        $('.reply_form').hide();
                        $('.reply_input').value("")
                    }else{
                        alert(resp.errmsg)
                    }
                }
            })
        }
    });

        // 关注当前新闻作者
    $(".focus").click(function () {
        var author_id = $('.author_name').attr('author_id')
        var action = 'focus'
        var params = {
            "author_id": author_id,
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
                    $('.focus').hide();
                    $('.focused').show()
                }else{
                    alert(resp.errmsg)
                }
            }
        })
    })

    // 取消关注当前新闻作者
    $(".focused").click(function () {
        var author_id = $('.author_name').attr('author_id')
        var action = 'cancel_focus'
        var params = {
            "author_id": author_id,
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
                    $('.focus').show();
                    $('.focused').hide()
                }else{
                    alert(resp.errmsg)
                }
            }
        })
    })
})