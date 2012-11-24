LionFace.Notification = function(options) {
    this.options = $.extend({
        
    }, options || {});;
    this.init();
};

LionFace.Notification.prototype = {

    init: function() {
        this.bind_load_content();
        this.bind_mark_notification();
        this.bind_nav();
        this.reset_notificaton_count();
    },

    reset_notificaton_count: function() {  
        if ($('#notifications_id_notif span').length) {
            $('#notifications_id_notif span').remove();
        }
    },

    load_post: function(post, type, model) { 
        var url = "/posts/show/";
        var model = model || '';
        var $elem = $('.right_content');

        $elem.html("").addClass("large_loader"); 
        make_request({
            url: url,
            data: {
                post_id: post,
                post_type: type,
                post_model: model,
            },
            callback: function(data) {
                $elem.removeClass("large_loader")
                if (data.html != undefined) {
                    $elem.html(data.html);
                    make_excerpts();
                }
            },
            errorback: function() {
                $elem.removeClass("large_loader");
                alert('Unable to retrieve data.');
            },
        });
    },

    load_image_comments: function(pk) {
        if (pk == undefined)
            return;
        var $elem = $('.right_content');
        $.ajax({
            url: '/images/notifications/',
            data: {
                'pk': pk,
            },
            beforeSend: function(jqXHR, settings) {
                $elem.html('').addClass('large_loader');
            },
            success: function(data, textStatus, jqXHR) {
                if (data.status == 'ok') {
                    $elem.html(data.html);
                    LionFace.User['images_comments_ajax'] = data.images_comments_ajax;
                    LionFace.Images.popup_comments_list($($elem.find('.image_container')));
                    LionFace.Images.popup_comments_bind_make_comment();
                } else {
                    this.error(jqXHR, textStatus);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                alert('Unable to retrieve data.');
            },
            complete: function(jqXHR, textStatus) {
                $elem.removeClass('large_loader');
            },
        });
        
    },

    bind_load_content: function() {
        var _this = this;
        var selectors = [
            '.profile_post',
            '.shared_post',
            '.comment_submitted',
            '.comment_image',
            '.follow_comment',
            '.follow_shared',
        ];

        $(document).on('click', selectors.join(','), function(e) {
            var starter = document.elementFromPoint(e.clientX, e.clientY);
            if ($(starter).is('a')) {
                return;
            }
            var meta = $(this).metadata();
            if (meta.id) {
                if ($(this).hasClass('comment_image')) {
                    _this.load_image_comments(meta.id);
                } else {
                    _this.load_post(meta.id, meta.type, meta.model)
                }
            } else {
                $('.right_content').html("");
            }
        });
    },

    bind_mark_notification: function() {
        $(document).on('click', '.notification', function(e) {
            if ($(this).find('.new_notification').length) {
                $(this).find('.new_notification').removeClass('new_notification');
            }
        });
    },

    bind_nav: function() {
        $(document).on('click', '.nav_link', function() { 
            $.ajax({
                type: 'GET',
                url: $(this).attr('href'),
                success: function(data) {
                    $('.left_col').replaceWith(data);
                },
                error: function() {
                    console.log('fail');
                },
            });
            return false;
        });
    },

};

$(function() {         
    LionFace.Notification = new LionFace.Notification();
});
