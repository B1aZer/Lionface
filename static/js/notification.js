LionFace.Notification = function(options) {
    this.options = $.extend({

    }, options || {});
    this.init();
};

LionFace.Notification.prototype = {

    init: function() {
        this.bind_load_content();
        this.bind_mark_notification();
        this.bind_nav();
        this.reset_notificaton_count();
        this.bind_other();
    },

    reset_notificaton_count: function() {
        if ($('#notifications_id_notif span').length) {
            $('#notifications_id_notif span').remove();
        }
    },

    toggle_comments: function() {
        $('.comment_counter').each( function(i,e) {
            if (get_int($(e).html()) > 0) {
                //$(e).parents('.toggle_comments').click();
                $(e).parents('.result').find('.comments').show();
            }
        });
    },

    load_post: function(post, type, model) {
        var cls = this;
        var url = "/posts/show/";
        var $elem = $('.right_content');
        model = model || '';

        $elem.html("").addClass("large_loader");
        make_request({
            url: url,
            data: {
                post_id: post,
                post_type: type,
                post_model: model
            },
            callback: function(data) {
                $elem.removeClass("large_loader");
                if (data.html !== undefined) {
                    $elem.html(data.html);
                    make_excerpts();
                    cls.toggle_comments();
                    LionFace.PostImages.bind_settings();
                }
            },
            errorback: function() {
                $elem.removeClass("large_loader");
                alert('Unable to retrieve data.');
            }
        });
    },

    load_image_comments: function(pk, owner_id, owner_type) {
        if (pk === undefined)
            return;
        var data = {'pk': pk};
        if (owner_id !== undefined && owner_type !== undefined) {
            data['owner_id'] = owner_id;
            data['owner_type'] = owner_type;
        }
        var $elem = $('.right_content');
        $.ajax({
            url: '/images/notifications/',
            data: data,
            beforeSend: function(jqXHR, settings) {
                $elem.html('').addClass('large_loader');
            },
            success: function(data, textStatus, jqXHR) {
                if (data.status == 'ok') {
                    $elem.html(data.html);
                    // ???: should this be post_images_comment_ajax?
                    LionFace.User['images_comments_ajax'] = data.images_comments_ajax;
                    if (data.owner === 'user') {
                        LionFace.Images.popup_comments_list($($elem.find('.image_container')));
                        LionFace.Images.popup_comments_bind_make_comment();
                    } else if (data.owner === 'post') {
                        LionFace.PostImages.popup_comments_list($($elem.find('.image_container')));
                        LionFace.PostImages.popup_comments_bind_make_comment();
                    }
                } else {
                    this.error(jqXHR, textStatus);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                alert('Unable to retrieve data.');
            },
            complete: function(jqXHR, textStatus) {
                $elem.removeClass('large_loader');
            }
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
            '.follow_shared'
        ];

        $(document).on('click', selectors.join(','), function(e) {
            console.log('hi');
            var starter = document.elementFromPoint(e.clientX, e.clientY);
            if ($(starter).is('a')) {
                return;
            }
            var meta = $(this).metadata();
            if (meta.id) {
                if ($(this).hasClass('comment_image')) {
                    if (meta.owner_type === '') {
                        _this.load_image_comments(meta.id);
                    } else {
                        _this.load_image_comments(meta.id, meta.owner_id, meta.owner_type);
                    }
                } else {
                    _this.load_post(meta.id, meta.type, meta.model);
                }
            } else {
                $('.right_content').html("");
            }
        });

        $(document).on('click', ".hide_notification", function(e) {
            e.preventDefault();
            var url = $(this).attr('href');
            var $this = $(this);
            make_request({
                url:url,
                callback: function(data) {
                    if (data.status == 'OK') {
                        $this.parents('.notification').hide();
                    }
                }
            });
        });

    },

    bind_mark_notification: function() {
        $(document).on('click', '.notification', function(e) {
            if ($(this).find('.new_notification').length) {
                $(this).find('.new_notification').removeClass('new_notification');
            }
            $('.active_notification').removeClass('active_notification');
            $(this).find('.link-output').addClass('active_notification');
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
                }
            });
            return false;
        });
    },

    bind_other : function () {
        $(document).on('click', '.relation_request_a', function(e) {
            e.preventDefault();
            var self = $(this);
            var url = self.attr('href');
            make_request({
                url:url,
                callback: function(data) {
                    if (data.status == 'OK') {
                        self.parents('.relation_request').fadeOut();
                    }
                }
            });
        });
    }
};

$(function() {
    LionFace.Notification = new LionFace.Notification();
});
