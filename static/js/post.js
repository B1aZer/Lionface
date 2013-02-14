LionFace.PostImages = function(options) {
    this.options = $.extend({
        'swap_images_delay': 500,
        'change_thumb_delay': 500,
        'popup_fadeDuration': 500,
    }, options || {});
    this.init();
};


LionFace.PostImages.prototype = {

    init : function() {
        this.$popup_posts = undefined;

        $('.post_image_popup').appendTo($('body'));

        // !!!: bind settings running in feed.js on loading feed
        // this.bind_settings();
        // binding now in post/_feed.html
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
            //console.log( $(selector) );
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
        if (count !== undefined) {
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
            $elem = $(elem);

        $elem.click(function() {
            $(this).attr('popup', true);
            _this.popup_start(elem, newsitem);
            return false;
        });
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
            //console.log($(next));
            this.popup_change_item($(next));
        }
    },

    popup_resize: function() {
        var $popup = $('.post_image_popup');
        $popup.css({
            top: $(window).scrollTop() + 'px',
            left: $(window).scrollLeft() + 'px'
        });
        $popup.find('.image_zone_view').width($popup.find('.image_zone').width() - 351);
        $popup.find('.image_zone_view').find('.prev, .next').css({
            'width': $popup.find('.image_zone').width()*0.2 + 'px'
        }).find('img').css({
            'margin-top': ($popup.find('.image_zone').height()-45)/2
        });
        //'margin-left': $popup.find('.image_zone').width() - 351 - $popup.find('.image_zone_view .rotate-right').find('img').width()
        $popup.find('.image_zone_view .rotate-right').css({
            'margin-left': $popup.find('.image_zone_view .rotate-left').find('img').width()
        });

        $popup.find('.image_zone_view .next').css({
            'margin-left': $popup.find('.image_zone').width()*(1 - 0.2) - 351
        });

        $popup.find('.image_zone_view .loader').css({
            'line-height': $popup.find('.image_zone').height() + 'px'
        });

        $popup.find('.image_zone_info .scroll_area').height(
            $popup.find('.image_zone_info').height() - $popup.find('.image_zone_info .close').height() - $popup.find('.image_zone_info .make_comment').height() - 15
        );
        var image = $popup.find('.image_zone_view .image img');
        if ($(image).length) {
            var winw = $popup.find('.image_zone_view').width();
            var winh = $popup.find('.image_zone_view').height();
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
            'margin-top': ($popup.find('.image_zone_view').height() - $(image).height()) / 2
        });
        return false;
    },

    popup_change_item: function(item, change) {
        if (item === undefined)
            return false;
        if (change === undefined)
            change = true;
        var _this = this;
        var meta = $(this.$popup_posts).metadata('username');
        var $popup = $('.post_image_popup');
        this.save_rotated_image();
        this.popup_resize();
        $('.image_container li[popup=true]').attr('popup', false);
        $(item).attr('popup', true);
        $popup.find('.image_zone_view').find('.prev, .next').hide().find('img').hide();
        $popup.find('.image_zone_view').find('.rotate-left, .rotate-right').hide().find('img').hide();
        $popup.find('.image_zone_view .image').hide().html('');
        $popup.find('.image_zone_view .loader').show();
        // load image
        var image = $('<img>');
        $(image).load(function() {
            $popup.find('.image_zone_view .loader').hide();
            $popup.find('.image_zone_view .image').show();
            if (meta.username == LionFace.User.username) {
                $popup.find('.image_zone_view').find('.rotate-left, .rotate-right').show();
            }
            $popup.find('.image_zone_view').find('.prev, .next').show();
            _this.popup_resize();
        });
        $popup.find('.image_zone_view .image').append( $(image) );
        var image_src = $(item).find('div.image_album').data('original-url'); 
        var n = image_src.indexOf('?');
        var d = new Date();
        // if no timestamp on image, add one
        if (n < 0) {
            image_src = image_src + '?' + d.getTime();
        }
        $(image).attr('src', image_src);
        // rotate image
        if ($(item).attr('data-rotated')) {
            //_this.image_angle = parseInt($(item).attr('data-rotated'));
            //_this.rotate_image($(image),_this.image_angle); 
        }
        // load comments
        this.popup_comments_list($(item));
        // make comment
        $popup.find('.image_zone_info .make_comment textarea').fadeOut(
            _this.options.popup_fadeDuration,
            function() {
                $(this).val('').fadeIn(_this.options.popup_fadeDuration);
            }
        );
        // toggle image following
        var follonwings = $(item).data('following');
        if ($.inArray(LionFace.User.username,follonwings) >= 0) {
            $popup.find('#add_post_follower').hide();
            $popup.find('#rem_post_follower').show();
        }
        else {
            $popup.find('#add_post_follower').show();
            $popup.find('#rem_post_follower').hide();
        }
        // toggle lovers
        var lovers = $(item).data('lovers');
        if ($.inArray(LionFace.User.username,lovers) >= 0) {
            $popup.find('#add_post_lovers').hide();
            $popup.find('#rem_post_lovers').show();
        }
        else {
            $popup.find('#add_post_lovers').show();
            $popup.find('#rem_post_lovers').hide();
        }
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

        $('.post_image_popup .image_zone, .post_image_popup .image_info').show();
        $('.post_image_popup').fadeIn(this.options.popup_fadeDuration);

        var owner = $('.post_image_popup .owner');
        owner.find('.user_absolute_url').prop('href', user_data.user_absolute_url);
        owner.find('.thumb').css('background', 'url(' + user_data.user_photo_thumb + ') #FFF');
        owner.find('.fullname').html(user_data.user_full_name);
        owner.find('.username').html(user_data.username);

        this.popup_enableKeyboard();
        this.popup_change_item(item, false);
        this.popup_start_overflow = $('body').css('overflow');
        $('body').css({'overflow': 'hidden'});
    },

    popup_end: function() {
        this.save_rotated_image();
        this.image_angle = undefined;
        this.$popup_posts = undefined;
        $('.post_image_popup .image_zone, .post_image_popup .image_info').hide();
        $('.post_image_popup').fadeOut(this.options.popup_fadeDuration);
        this.popup_disableKeyboard();
        $('body').css({'overflow': this.popup_start_overflow});
        this.popup_start_overflow = undefined;
    },

    rotate_image_left: function () {
        var _this = this;
        var angle = _this.image_angle || 0;
        var $popup = $('.post_image_popup');
        var image = $popup.find('.image_zone_view .image img');
        var cfangle = angle * 90 - 90;
        var ieangle = angle - 1;
        image.css({'-webkit-transform': 'rotate(' + cfangle + 'deg)',
                            '-moz-transform': 'rotate(' + cfangle + 'deg)',
                            'filter': 'progid:DXImageTransform.Microsoft.BasicImage(rotation=' + ieangle + ')'}); 
        _this.image_angle = ieangle;
    },

    rotate_image_right: function () {
        var _this = this;
        var angle = _this.image_angle || 0;
        var $popup = $('.post_image_popup');
        var image = $popup.find('.image_zone_view .image img');
        var cfangle = angle * 90 + 90;
        var ieangle = angle + 1;
        image.css({'-webkit-transform': 'rotate(' + cfangle + 'deg)',
                            '-moz-transform': 'rotate(' + cfangle + 'deg)',
                            'filter': 'progid:DXImageTransform.Microsoft.BasicImage(rotation=' + ieangle + ')'}); 
        _this.image_angle = ieangle;
    },

    save_rotated_image: function () {
        var _this = this;
        var d = new Date();
        var post = $(_this.$popup_posts);
        var item = post.find('li[popup=true]');
        var prev_angle_str = item.attr('data-rotated');
        if (prev_angle_str) {
            var prev_angle = parseInt(prev_angle_str);
        }
        if (_this.image_angle === undefined ) { return; }
        
        var angle = _this.image_angle;
        if (prev_angle) {
            angle = angle + prev_angle;
        }
        var cfangle = angle * 90;
        var ieangle = angle;
        var image = item.find('div');
        /*
        image.css({'-webkit-transform':'rotate(' + cfangle + 'deg)',
                            '-moz-transform': 'rotate(' + cfangle + 'deg)', 
                            'filter': 'progid:DXImageTransform.Microsoft.BasicImage(rotation=' + ieangle + ')'}); 
                            */
        // saving to db
        var url = LionFace.User['images_rotation'];
        make_request({ 
            url:url,
            multi:true,
            data: {'post-pk':item.attr('data-post-pk'),
                'image-pk':item.attr('data-pk'),
                'angle':_this.image_angle,
            },
            callback: function (data) {
                if (data.status == 'OK') {
                    // set timestamp fo immediate reload
                    var old_url = image.data('original-url');
                    var n = old_url.indexOf('?');
                    old_url = old_url.substring(0, n != -1 ? n : old_url.length);
                    var new_url = old_url + '?' + d.getTime();
                    image.data('original-url', new_url );

                    var old_src = image.css('backgroundImage');
                    old_src = old_src.replace('url(','').replace(')','');
                    n = old_src.indexOf('?');
                    old_src = old_src.substring(0, n != -1 ? n : old_src.length);
                    var new_src = old_src + '?' + d.getTime();
                    image.css('background', 'url(' + new_src + ') #D0D3D5');
                }
            }
        });
        // rotation save
        item.attr('data-rotated', angle);
        _this.image_angle = undefined;
    },

    rotate_image: function (image, angle) {
        var cfangle = angle * 90;
        var ieangle = angle;
        image.css({'-webkit-transform':'rotate(' + cfangle + 'deg)',
                            '-moz-transform': 'rotate(' + cfangle + 'deg)', 
                            'filter': 'progid:DXImageTransform.Microsoft.BasicImage(rotation=' + ieangle + ')'});
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

    post_lovers: function(e, el) {
        e.preventDefault();
        var _this = this;
        var $this = el;
        var $ul = $('.image_comments ul');
        var id = $this.attr('id');
        var url = $this.attr('href');
        var post = $(_this.$popup_posts);
        var item = post.find('li[popup=true]');
        var followings = item.data('following');
        var data = {
            'user': LionFace.User.username,
            'imagepk': $ul.data('image-pk')
            }
        if (id == 'add_post_lovers') {
            data['add'] = true;
        }
        else {
            data['add'] = false;
        }
        make_request({ 
            url:url,
            data:JSON.stringify(data),
            callback: function (data) {
                if (data.status == 'OK') {
                    if (data.rem) {
                        var index = followings.indexOf(LionFace.User.username);
                        followings.splice(index, 1);
                        $('#rem_post_lovers').hide();
                        $('#add_post_lovers').show();
                    }
                    else {
                        followings.push(LionFace.User.username);
                        $('#rem_post_lovers').show();
                        $('#add_post_lovers').hide();
                    }
                    item.data('lovers',followings)
                }
            }
        });
    },

    post_followers: function(e, el) {
        e.preventDefault();
        var _this = this;
        var $this = el;
        var $ul = $('.image_comments ul');
        var id = $this.attr('id');
        var url = $this.attr('href');
        var post = $(_this.$popup_posts);
        var item = post.find('li[popup=true]');
        var followings = item.data('following');
        var data = {
            'user': LionFace.User.username,
            'imagepk': $ul.data('image-pk')
            }
        if (id == 'add_post_follower') {
            data['add'] = true;
        }
        else {
            data['add'] = false;
        }
        make_request({ 
            url:url,
            data:JSON.stringify(data),
            callback: function (data) {
                if (data.status == 'OK') {
                    if (data.rem) {
                        var index = followings.indexOf(LionFace.User.username);
                        followings.splice(index, 1);
                        $('#rem_post_follower').hide();
                        $('#add_post_follower').show();
                    }
                    else {
                        followings.push(LionFace.User.username);
                        $('#add_post_follower').hide();
                        $('#rem_post_follower').show();
                    }
                    item.data('following',followings)
                }
            }
        });
    },

    popup_comments_delete: function($item) {
        var _this = this,
            $ul = $('.post_image_popup .image_comments ul');

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
        var $popup = $('.post_image_popup');
        $(window).on('resize', this.popup_resize);
        $(document).on('resize', this.popup_resize);
        $popup.find('.image_overlay').click(function() {
            _this.popup_end();
            return false;
        });
        $popup.find('.image_zone_info .close a').click(function() {
            _this.popup_end();
            return false;
        });
        // arrows
        $popup.find('.image_zone_view').find('.prev, .next').hover(
            function(event) {
                if ($('.image_container li[popup=true]').siblings('li').length > 0) {
                    $(this).find('img').fadeIn(_this.options.popup_fadeDuration);
                }
            },
            function(event) {
                if ($('.image_container li[popup=true]').siblings('li').length > 0) {
                    $(this).find('img').fadeOut(_this.options.popup_fadeDuration);
                }
            }
        ).mousemove(function(event) {
            if ($('.image_container li[popup=true]').siblings('li').length > 0) {
                $(this).find('img').fadeIn(_this.options.popup_fadeDuration);
            }
        });
        $popup.find('.image_zone_view').mousemove(
            function(event) {
                $(this).find('.rotate-left, .rotate-right').find('img').fadeIn(_this.options.popup_fadeDuration);
            }
        ).mouseleave(
            function(event) {
                $(this).find('.rotate-left, .rotate-right').find('img').fadeOut(_this.options.popup_fadeDuration);
            } 
        );
        $popup.find('.image_zone_view .prev').click(function(event) {
            _this.popup_to_prev();
        });
        $popup.find('.image_zone_view .next').click(function(event) {
            _this.popup_to_next();
        });
        $popup.find('.image_zone_view .rotate-left').click(function(event) {
            _this.rotate_image_left();
        });
        $popup.find('.image_zone_view .rotate-right').click(function(event) {
            _this.rotate_image_right();
        });
        $popup.find('.post_followers').click(function(e) {
            _this.post_followers(e, $(this));
        });
        $popup.find('.post_lovers').click(function(e) {
            _this.post_lovers(e, $(this));
        });
        this.popup_comments_bind_make_comment();
    }
};

$(function() {
    LionFace.PostImages = new LionFace.PostImages();
});
