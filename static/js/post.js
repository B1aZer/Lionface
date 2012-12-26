//@ sourceURL=post.js

LionFace.PostImages = function(options) {
    this.options = $.extend({
        'swap_images_delay': 500,
        'change_thumb_delay': 500,
        'popup_fadeDuration': 500
    }, options || {});
    this.init();
};


LionFace.PostImages.prototype = {

    init : function() {
        this.$popup_posts = undefined;

        $('.image_popup').appendTo($('body'));

        // !!!: bind settings running in feed.js on loading feed
        // this.bind_settings();
        this.bind_popup();
    },

    bind_settings: function($post) {
        var _this = this;
        if ($post !== undefined) {
            $post.find('li').each(function(index, elem) {
                _this.create_settings(elem, $post);
            });
        } else {
            $('.post_feed').each(function(index, newsitem) {
                $(newsitem).find('li').each(function(index, elem) {
                    _this.create_settings(elem, newsitem);
                });
            });
        }
    },

    set_new_thumb: function(src) {
        var _this = this,
        selector = '.images_'+LionFace.User['images_type']+'_thumb';
        if (src !== undefined) {
            var src = $('<div></div>').css({
                'backgroundImage': 'url('+src+')'
            }).css('backgroundImage');
            console.log( $(selector) );
            $(selector).each(function(index, elem) {
                if ($(this).css('backgroundImage') == src)
                    return;
                $(elem).animate({
                    'opacity': 0,
                }, _this.options.change_thumb_delay, function() {
                    $(this).css({
                        'backgroundImage': src,
                    }).animate({
                        'opacity': 1,
                    }, _this.options.change_thumb_delay);
                });
            });
        }
    },

    set_photos_count: function(count) {
        if (count != undefined) {
            var $elem = $('#photos_count');
            if ($elem.html() != count) {
                $elem.fadeOut(function() {
                    $(this).html(count).fadeIn();
                });
            }
        }
    },

    create_settings: function(elem, newsitem) {
        var _this = this,
            $elem = $(elem),
        $image_settings = $elem.find('#image_settings');

        $elem.click(function() {
            $(this).attr('popup', true);
            _this.popup_start(elem, newsitem);
            return false;
        });
        if ($image_settings.length != 1)
            return;
        $image_settings.hide();
        $elem.find('.image_album').hover(
            function() {
                $image_settings.show();
            },
            function() {
                $image_settings.hide();
            }
        );
        /*
        if ($image_settings.find('#make_primary').data('activity') == 1) {
            $image_settings.find('#make_primary').hide();
        } else {
            $image_settings.find('#make_primary').show();
        }
        $image_settings.find('#make_primary').click(function() {
            $.ajax({
                url: LionFace.User['images_ajax'],
                type: 'POST',
                data: {
                    'method': 'activity',
                    'pk': $elem.data('pk'),
                },
                success: function(data, textStatus, jqXHR) {
                    if ( data.status == 'ok' ) {
                        var $li1 = $elem;
                        var $li2 = $('.image_container li:first');
                        $li1.find('#make_primary').data('activity', '1');
                        $li1.find('#make_primary').hide();
                        if ( !$li1.is($li2) ) {
                            $li2.find('#make_primary').data('activity', '0');
                            $li2.find('#make_primary').show();
                        }
                        _this.set_positions_images( data.positions, false );
                        _this.swap_images($li1, $li2).then(function() {
                            _this.sort_images();
                        });
                        _this.set_new_thumb(data.thumb_src);
                        _this.set_photos_count(data.photos_count);
                    }
                }
            });
            return false;
        });
        $image_settings.find('#delete').click(function() {
            $.ajax({
                url: LionFace.User['images_ajax'],
                type: 'POST',
                data: {
                    'method': 'delete',
                    'pk': $elem.data('pk'),
                    'row': LionFace.User['images_now_rows']
                },
                success: function(data, textStatus, jqXHR) {
                    if ( data.status == 'ok' ) {
                        var $li = $elem, $ul = $elem.parent();
                        $ul.animate({
                            'opacity': 0
                        }, 500, function() {
                            $li.remove();
                            if (data.html !== undefined) {
                                var $item = $(data.html).filter('li');
                                if ($item.data('pk') != $ul.find('li:last').data('pk')) {
                                    _this.create_settings($item);
                                    $ul.find('li:last').after($item);
                                }
                            }
                            _this.set_positions_images(data.positions);
                            $ul.animate({
                                'opacity': 1
                            }, 500);
                        });
                        _this.set_new_thumb(data.thumb_src);
                        _this.set_photos_count(data.photos_count);
                    }
                }
            });
            return false;
        });
*/
    },

    swap_images: function(li1, li2, delay) {
        if (li1 == undefined || li2 == undefined)
            return false;
        if ( delay == undefined )
            delay = this.options.swap_images_delay;
        var d = $.Deferred(),
        $li1 = $(li1),
        $li2 = $(li2);
        if (delay == 0) {
            if ( !$li1.is($li2) ) {
                var $point = $('<span></span>').hide();
                $li1.after( $point );
                $li2.after( $li1 );
                $point.after( $li2 );
                $point.remove();
            }
            d.resolve();
        } else {
            if ( $li1.is($li2) ) {
                $li1.animate({
                    'opacity': 0,
                }, delay, '', function() {
                    $li1.animate({
                        'opacity': 1,
                    }, delay, '', function() {
                        d.resolve();
                    });
                });
            } else {
                var ds = new Array();
                for (var i = 0; i < 4; ++i)
                    ds.push($.Deferred());
                $li1.animate({
                    'opacity': 0,
                }, delay, '', function() {
                    ds[0].resolve();
                });
                $li2.animate({
                    'opacity': 0,
                }, delay, '', function() {
                    ds[1].resolve();
                });
                $.when(ds[0], ds[1]).then(function() {
                    var $point = $('<span></span>').hide();
                    $li1.after( $point );
                    $li2.after( $li1 );
                    $point.after( $li2 );
                    $point.remove();
                    $li1.animate({
                        'opacity': 1,
                    }, delay, '', function() {
                        ds[2].resolve();
                    });
                    $li2.animate({
                        'opacity': 1,
                    }, delay, '', function() {
                        ds[3].resolve();
                    });
                });
                d = $.when(ds[2], ds[3]);
            }
        }
        return d;
    },

    set_positions_images: function(data, resort) {
        if (data === undefined)
            return false;
        if (resort === undefined)
            resort = true;
        $('.image_container li').each(function(index, elem) {
            $(elem).data('position', data[$(elem).data('pk')]);
        });
        if (resort)
            this.sort_images();
    },

    /** popup functions */

    popup_enableKeyboard: function(options) {
        var _this = this;
        options = $.extend({
            esc_only: false
        }, options || {});
        function keyboard(event) {
            var KEYCODE_ESC = 27;
            var KEYCODE_LEFTARROW = 37;
            var KEYCODE_RIGHTARROW = 39;
            var keycode = event.keyCode;
            var key = String.fromCharCode(keycode).toLowerCase();
            if (keycode === KEYCODE_ESC) {
                _this.popup_end();
            }
            if (!options.esc_only) {
                if (key === 'p' || keycode === KEYCODE_LEFTARROW) {
                    _this.popup_to_prev();
                } else if (key === 'n' || keycode === KEYCODE_RIGHTARROW) {
                    _this.popup_to_next();
                }
            }
        }
        this.popup_disableKeyboard();
        $(document).on('keyup.keyboard', keyboard);
    },

    popup_disableKeyboard: function() {
        $(document).off('.keyboard');
    },

    popup_to_prev: function() {
        var now = $('.image_container li[popup=true]', this.$popup_posts);
        var next;
        if ($('.image_container li', this.$popup_posts).length > 1) {
            if ($(now).prev().length > 0) {
                next = $(now).prev();
            } else {
                next = $('.image_container li:last', this.$popup_posts);
            }
            this.popup_change_item($(next));
        }
    },

    popup_to_next: function() {
        var now = $('.image_container li[popup=true]', this.$popup_posts);
        var next;
        if ($('.image_container li', this.$popup_posts).length > 1) {
            if ($(now).next().length > 0) {
                next = $(now).next();
            } else {
                next = $('.image_container li:first', this.$popup_posts);
            }
            console.log($(next));
            this.popup_change_item($(next));
        }
    },

    popup_resize: function() {
        $('.image_popup').css({
            top: $(window).scrollTop() + 'px',
            left: $(window).scrollLeft() + 'px'
        });
        $('.image_zone_view').width($('.image_zone').width() - 351);
        $('.image_zone_view').find('.prev, .next').css({
            'width': $('.image_zone').width()*0.2 + 'px'
        }).find('img').css({
            'margin-top': ($('.image_zone').height()-45)/2
        });
        $('.image_zone_view .next').css({
            'margin-left': $('.image_zone').width()*(1 - 0.2) - 351
        });
        $('.image_zone_view .loader').css({
            'line-height': $('.image_zone').height() + 'px'
        });
        $('.image_zone_info .scroll_area').height(
            $('.image_zone_info').height() - $('.image_zone_info .close').height() - $('.image_zone_info .make_comment').height() - 15
        );
        var image = $('.image_zone_view .image img');
        if ($(image).length) {
            var winw = $('.image_zone_view').width();
            var winh = $('.image_zone_view').height();
            var ratioX, ratioY, scale, newWidth, newHeight;

            ratioX = winw / $(image).width();
            ratioY = winh / $(image).height();
            scale = ratioX < ratioY ? ratioX : ratioY;
            newWidth = parseInt($(image).width() * scale, 10);
            newHeight = parseInt($(image).height() * scale, 10);
            $(image).css({
                "width": newWidth + "px",
                "height": newHeight + "px"
            }).attr({
                "width": newWidth,
                "height": newHeight
            });
        }
        $(image).css({
            'margin-top': ($('.image_zone_view').height() - $(image).height()) / 2
        });
        return false;
    },

    popup_change_item: function(item, change) {
        if (item === undefined)
            return false;
        if (change === undefined)
            change = true;
        var _this = this;
        this.popup_resize();
        $('.image_container li[popup=true]').attr('popup', false);
        $(item).attr('popup', true);
        $('.image_zone_view').find('.prev, .next').hide().find('img').hide();
        $('.image_zone_view .image').hide().html('');
        $('.image_zone_view .loader').show();
        // load image
        var image = $('<img>');
        $(image).load(function() {
            $('.image_zone_view .loader').hide();
            $('.image_zone_view .image').show();
            $('.image_zone_view').find('.prev, .next').show();
            _this.popup_resize();
        });
        $('.image_zone_view .image').append( $(image) );
        $(image).attr('src', $(item).find('div.image_album').data('original-url'));
        // load comments
        this.popup_comments_list($(item));
        // make comment
        $('.image_zone_info .make_comment textarea').fadeOut(
            _this.options.popup_fadeDuration,
            function() {
                $(this).val('').fadeIn(_this.options.popup_fadeDuration);
            }
        );
    },

    popup_start: function(item, newsitem) {
        var user_data = $(newsitem).metadata();

        this.$popup_posts = newsitem;
        // var album_name = $(newsitem).find('.album_name').html();
        // if (album_name === '') {
        // } else {
        //     var $related_posts = $('.post_feed .album_name:contains("'
        //         + album_name + '")').closest('.result');
        //     this.$popup_posts = $related_posts;
        // }
        // console.log(this.$popup_posts);

        $('.image_popup .image_zone, .image_popup .image_info').show();
        $('.image_popup').fadeIn(this.options.popup_fadeDuration);

        var owner = $('.image_popup .owner');
        owner.find('.user_absolute_url').prop('href', user_data.user_absolute_url);
        owner.find('.thumb').css('background', 'url(' + user_data.user_photo_thumb + ') #FFF');
        owner.find('.fullname').html(user_data.user_full_name);
        owner.find('.username').html(user_data.username);

        this.popup_enableKeyboard();
        this.popup_change_item(item, false);
        this.popup_start.overflow = $('body').css('overflow');
        $('body').css({'overflow': 'hidden'});
    },

    popup_end: function() {
        this.$popup_posts = undefined;
        $('.image_popup .image_zone, .image_popup .image_info').hide();
        $('.image_popup').fadeOut(this.options.popup_fadeDuration);
        this.popup_disableKeyboard();
        $('body').css({'overflow': this.popup_start.overflow});
        this.popup_start.overflow = undefined;
    },

    popup_comments_refresh: function($comments) {
        var _this = this,
        $ul = $('.image_comments ul');
        $ul.fadeOut(200, function() {
            $ul.html('');
            $comments.each(function(index, item) {
                var $item = $(item);
                $ul.prepend($item);
                if ($item.find('div.delete').length > 0) {
                    $item.hover(
                        function(event) {
                            $item.find('div.delete').show();
                        },
                        function(event) {
                            $item.find('div.delete').hide();
                        }
                    ).find('div.delete').click(function(event) {
                        _this.popup_comments_delete($item);
                        return false;
                    });
                }
            });
            $ul.fadeIn(200);
        });
    },

    popup_comments_bind_make_comment: function() {
        var _this = this;
        $('.make_comment textarea').autosize({
            callback: function(ta) {
                _this.popup_resize();
            }
        }).focusin(function(event) {
            _this.popup_enableKeyboard({
                esc_only: true
            });
        }).focusout(function(event) {
            _this.popup_enableKeyboard();
        }).keydown(function(event){
            var
            KEYCODE_ENTER = 13,
            keycode = event.keyCode;
            if (keycode == KEYCODE_ENTER) {
                _this.popup_comments_add($(this));
                return false;
            }
        });
    },

    popup_comments_add: function($textarea) {
        var _this = this,
            $ul = $('.image_comments ul'),
            val = $textarea.val();
        if (val.length < 1)
            return;
        $.ajax({
            url: LionFace.User['images_comments_ajax'],
            type: 'POST',
            data: {
                'method': 'create',
                'message': val,
                'image-pk': $ul.data('image-pk'),
                'post-pk': $ul.data('post-pk')
            },
            beforeSend: function(jqXHR, settings) {
                $textarea.data('val', val);
                $textarea.val(' ');
                $textarea.prop('disabled', true);
            },
            success: function(data, textStatus, jqXHR) {
                if (data.status == 'ok') {
                    $textarea.val('');
                    _this.popup_comments_refresh($(data.comments).filter('li'));
                } else {
                    this.error(jqXHR, textStatus);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                $textarea.val($textarea.data('val'));
            },
            complete: function(jqXHR, textStatus) {
                $textarea.prop('disabled', false);
            }
        });
    },

    popup_comments_list: function($item) {
        var _this = this,
            $ul = $('.image_comments ul');
        $ul.data('image-pk', $item.data('pk'));
        $ul.data('post-pk', $item.data('post-pk'));
        $.ajax({
            url: LionFace.User['images_comments_ajax'],
            data: {
                'method': 'list',
                'image-pk': $ul.data('image-pk'),
                'post-pk': $ul.data('post-pk')
            },
            beforeSend: function(jqXHR, settings) {
                $ul.html('');
            },
            success: function(data, textStatus, jqXHR) {
                if (data.status == 'ok') {
                    _this.popup_comments_refresh($(data.comments).filter('li'));
                }
            }
        });
    },

    popup_comments_delete: function($item) {
        var _this = this,
            $ul = $('.image_comments ul');

        $.ajax({
            url: LionFace.User['images_comments_ajax'],
            type: 'POST',
            data: {
                'method': 'delete',
                'comment_pk': $item.data('pk'),
                'post-pk': $ul.data('post-pk'),
                'image-pk': $ul.data('image-pk')
            },
            success: function(data, textStatus, jqXHR) {
                if (data.status == 'ok') {
                    _this.popup_comments_refresh($(data.comments).filter('li'));
                }
            }
        });
    },

    bind_popup: function() {
        var _this = this;
        $(window).on('resize', this.popup_resize);
        $(document).on('resize', this.popup_resize);
        $('.image_overlay').click(function() {
            _this.popup_end();
            return false;
        });
        $('.image_zone_info .close a').click(function() {
            _this.popup_end();
            return false;
        });
        // arrows
        $('.image_zone_view').find('.prev, .next').hover(
            function(event) {
                if ($('.image_container li').length > 1) {
                    $(this).find('img').fadeIn(_this.options.popup_fadeDuration);
                }
            },
            function(event) {
                if ($('.image_container li').length > 1) {
                    $(this).find('img').fadeOut(_this.options.popup_fadeDuration);
                }
            }
        ).mousemove(function(event) {
            if ($('.image_container li').length > 1) {
                $(this).find('img').fadeIn(_this.options.popup_fadeDuration);
            }
        });
        $('.image_zone_view .prev').click(function(event) {
            _this.popup_to_prev();
        });
        $('.image_zone_view .next').click(function(event) {
            _this.popup_to_next();
        });
        this.popup_comments_bind_make_comment();
    }

};

$(function() {
    LionFace.PostImages = new LionFace.PostImages();
});