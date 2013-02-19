LionFace.Images = function(options) {
    this.options = $.extend({
        'swap_images_delay': 500,
        'change_thumb_delay': 500,
        'popup_fadeDuration': 500
    }, options || {});
    this.init();
};


LionFace.Images.prototype = {

    init : function() {
        var _this = this;
        $('.image_popup').appendTo($('body'));
        $('.image_container li').each(function(index, elem) {
            _this.create_settings(elem);
        });
        if (!LionFace.User.is_anonymous && LionFace.User.images_manage) {
            this.sort_images();
            this.bind_sorting();
        }
        this.bind_popup();
        this.bind_view_more_button();
        this.load_quote();
    },

    set_new_thumb: function(src) {
        var _this = this,
        selector = '.images_'+LionFace.User['images_type']+'_thumb';
        if (src !== undefined) {
            src = $('<div></div>').css({
                'backgroundImage': 'url('+src+')'
            }).css('backgroundImage');
            console.log( $(selector) );
            $(selector).each(function(index, elem) {
                if ($(this).css('backgroundImage') == src)
                    return;
                $(elem).animate({
                    'opacity': 0
                }, _this.options.change_thumb_delay, function() {
                    $(this).css({
                        'backgroundImage': src
                    }).animate({
                        'opacity': 1
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

    create_settings: function(elem) {
        var _this = this,
        $elem = $(elem),
        $image_settings = $elem.find('#image_settings');

        $elem.click(function() {
            $(this).attr('popup', true);
            _this.popup_start(elem);
            return false;
        });
        if ($image_settings.length != 1)
            return;
        $image_settings.hide();
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
                    'pk': $elem.data('pk')
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
    },

    swap_images: function(li1, li2, delay) {
        if (li1 === undefined || li2 === undefined)
            return false;
        if ( delay === undefined )
            delay = this.options.swap_images_delay;
        var d = $.Deferred(),
        $li1 = $(li1),
        $li2 = $(li2);
        if (delay === 0) {
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
                    'opacity': 0
                }, delay, '', function() {
                    $li1.animate({
                        'opacity': 1
                    }, delay, '', function() {
                        d.resolve();
                    });
                });
            } else {
                var ds = [];
                for (var i = 0; i < 4; ++i)
                    ds.push($.Deferred());
                $li1.animate({
                    'opacity': 0
                }, delay, '', function() {
                    ds[0].resolve();
                });
                $li2.animate({
                    'opacity': 0
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
                        'opacity': 1
                    }, delay, '', function() {
                        ds[2].resolve();
                    });
                    $li2.animate({
                        'opacity': 1
                    }, delay, '', function() {
                        ds[3].resolve();
                    });
                });
                d = $.when(ds[2], ds[3]);
            }
        }
        return d;
    },

    sort_images: function() {
        var selector = '.image_container li';
        var _this = this;
        function swap(elem1, elem2) {
            _this.swap_images(elem1, elem2, 0);
        }
        function cmp_images(a, b) {
            a = parseInt($(a).data('position'), 10);
            b = parseInt($(b).data('position'), 10);
            if (a > b) return 1;
            if (a < b) return -1;
            return 0;
        }
        function qsort(left, right) {
            var l = left, r = right;
            var c = Math.round((l+r)/2);
            while (l <= r) {
                while (cmp_images($(selector).get(l), $(selector).get(c)) == -1)
                    l++;
                while (cmp_images($(selector).get(r), $(selector).get(c)) == 1)
                    r--;
                if (l <= r) {
                    swap($(selector).get(l), $(selector).get(r));
                    l++;
                    r--;
                }
            }
            if (left < r)
                qsort(left, r);
            if (l < right)
                qsort(l, right);
        }
        qsort(0, $(selector).length-1);
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

    bind_sorting: function() {
        var _this = this;
        var pos_bgn;
        $('.image_container ul').sortable({
            start: function(event, ui) {
                pos_bgn = ui.item.index();
            },
            stop: function(event, ui) {
                if (pos_bgn == ui.item.index())
                    return;
                var pos_end = ui.item.index(),
                $item1 = $($('.image_container li').get(pos_bgn)),
                $item2 = $($('.image_container li').get(pos_end));
                if ((pos_bgn === 0 && $item2.find('#make_primary').data('activity') == 1) ||
                    (pos_bgn == 1 && $item1.find('#make_primary').data('activity') == 1)) {
                    $('.image_container ul').sortable('cancel');
                } else {
                    if (pos_bgn >= 2 && pos_end === 0 &&
                         $($('.image_container li').get(1)).find('#make_primary').data('activity') == 1) {
                        _this.swap_images($item2, $($('.image_container li').get(1)), 0);
                        pos_end = 1;
                        $item2 = $($('.image_container li').get(pos_end));
                    }
                    if (pos_bgn > pos_end)
                        $item1 = $item2.next();
                    if (pos_bgn < pos_end)
                        $item1 = $item2.prev();
                    $.ajax({
                        url: LionFace.User['images_ajax'],
                        type: 'POST',
                        data: {
                            'method': 'change_position',
                            'pk': $item2.data('pk'),
                            'instead': $item1.data('pk')
                        },
                        success: function(data, textStatus, jqXHR) {
                            if (data.status == 'ok') {
                                _this.set_positions_images(data.positions);
                                _this.set_new_thumb(data.thumb_src);
                                _this.set_photos_count(data.photos_count);
                            } else {
                                _this.sort_images();
                            }
                        },
                        error: function(jqXHR, textStatus, errorThrown) {
                            _this.sort_images();
                        }
                    });
                }
            }
        }).disableSelection();
    },

    bind_view_more_button: function() {
        var _this = this;
        var view_more = $('.image_container .view_more');
        if ( LionFace.User['images_now_rows'] >= LionFace.User['images_total_rows'] ) {
            $(view_more).hide();
        } else {
            $(view_more).show();
            $(view_more).find('a').click(function() {
                $.ajax({
                    url: LionFace.User['images_ajax'],
                    data: {
                        'method': 'more',
                        'row': LionFace.User['images_now_rows']
                    },
                    beforeSend: function(jqXHR, settings) {
                        $(view_more).find('.view_more_loader').fadeIn(250);
                    },
                    success: function(data, textStatus, jqXHR) {
                        if ( data.status == 'ok' ) {
                            LionFace.User['images_now_rows']++;
                            LionFace.User['images_total_rows'] = data.total_rows;
                            if ( LionFace.User['images_now_rows'] >= LionFace.User['images_total_rows'] ) {
                                $(view_more).fadeOut(500);
                            }
                            var $items = $(data.html).filter('li');
                            $items.each(function(index, elem) {
                                _this.create_settings(elem);
                                $(elem).css({'opacity': 0});
                            });
                            $('.image_container li:last').after($items);
                            $items.each(function(index, elem) {
                                $(elem).animate({'opacity': 1}, 1000);
                            });
                            _this.set_positions_images(data.positions);
                            _this.set_new_thumb(data.thumb_src);
                            _this.set_photos_count(data.photos_count);
                        }
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        $(view_more).prepend('<div class="error" style="font-size: 20px;">' + errorThrown + '</div>');
                        setTimeout(function() {
                            setTimeout(function() {
                                $(view_more).find('.error').remove();
                            }, 500);
                            $(view_more).find('.error').fadeOut(500);
                        }, 5000);
                    },
                    complete: function(jqXHR, textStatus) {
                        $(view_more).find('.view_more_loader').fadeOut(500);
                    }
                });
                return false;
            });
        }
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
        var now = $('.image_container li[popup=true]');
        var next;
        if ($('.image_container li').length > 1) {
            if ($(now).prev().length > 0) {
                next = $(now).prev();
            } else {
                next = $('.image_container li:last');
            }
            this.popup_change_item($(next));
        }
    },

    popup_to_next: function() {
        var now = $('.image_container li[popup=true]');
        var next;
        if ($('.image_container li').length > 1) {
            if ($(now).next().length > 0) {
                next = $(now).next();
            } else {
                next = $('.image_container li:first');
            }
            this.popup_change_item($(next));
        }
    },

    popup_resize: function() {
        var $popup = $('.image_popup');
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
        $popup.find('.image_zone_view .next').css({
            'margin-left': $popup.find('.image_zone').width()*(1 - 0.2) - 351
        });
        $popup.find('.image_zone_view .rotate-right').css({
            'margin-left': $popup.find('.image_zone_view .rotate-left').find('img').width()
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
        var $popup = $('.image_popup');
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
            $popup.find('.image_zone_view').find('.prev, .next').show();
            // privacy
            if (LionFace.User.images_manage) {
                $popup.find('.image_zone_view').find('.rotate-left, .rotate-right').show();
            }
            _this.popup_resize();
        });
        $popup.find('.image_zone_view .image').append( $(image) );
        $(image).attr('src', $(item).find('div.image_album').data('original-url'));
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
        // lovers
        var lovers = $(item).data('lovers');
        if ($.inArray(LionFace.User.username,lovers) >= 0) {
            $popup.find('#add_post_lovers').hide();
            $popup.find('#rem_post_lovers').show();
        }
        else {
            $popup.find('#add_post_lovers').show();
            $popup.find('#rem_post_lovers').hide();
        }
        //loves count
        var love_count = parseInt($(item).data('loves'));
        if (love_count == 0) {
            $popup.find('.loves_count').hide();
        }
        else {
            $popup.find('.loves_count').show();
        }
        $popup.find('.loves_count').html(love_count);
        // owner name
        var name = $(item).data('owner_name');
        var username = $(item).data('owner_username');
        var owner = $('.image_popup .owner');

        if (name) {
            owner.find('.fullname').html(name);
        }
        if (username) {
            owner.find('.username').html(username);
        }

    },

    popup_start: function(item) {
        $('.image_popup .image_zone, .image_popup .image_info').show();
        $('.image_popup').fadeIn(this.options.popup_fadeDuration);

        this.popup_enableKeyboard();
        this.popup_change_item(item, false);
        this.popup_start.overflow = $('body').css('overflow');
        $('body').css({'overflow': 'hidden'});
    },

    popup_end: function() {
        this.save_rotated_image();
        this.image_angle = undefined;
        $('.image_popup .image_zone, .image_popup .image_info').hide();
        $('.image_popup').fadeOut(this.options.popup_fadeDuration);
        this.popup_disableKeyboard();
        $('body').css({'overflow': this.popup_start.overflow});
        this.popup_start.overflow = undefined;
    },

    rotate_image_left: function () {
        var _this = this;
        var angle = _this.image_angle || 0;
        var $popup = $('.image_popup');
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
        var $popup = $('.image_popup');
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
        var post = $('.image_container');
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
        var image = item.find('.image_album');
        /*
        console.log(cfangle);
        image.css({'-webkit-transform':'rotate(' + cfangle + 'deg)',
                            '-moz-transform': 'rotate(' + cfangle + 'deg)', 
                            'filter': 'progid:DXImageTransform.Microsoft.BasicImage(rotation=' + ieangle + ')'}); 
                            */
        // saving to db
        var url = LionFace.User['images_rotation'];
        make_request({ 
            url:url,
            multi:true,
            data: {'image-pk':item.attr('data-pk'),
                'angle':_this.image_angle,
            },
            callback: function (data) {
                if (data.status == 'OK') {
                    // set timestamp fo immediate reload
                    var old_url = image.data('original-url');
                    var n = old_url.indexOf('?');
                    old_url = old_url.substring(0, n != -1 ? n : old_url.length);
                    var new_url = old_url + '?' + d.getTime();
                    console.log(new_url);
                    image.data('original-url', new_url );

                    var old_src = image.css('backgroundImage');
                    old_src = old_src.replace('url(','').replace(')','');
                    n = old_src.indexOf('?');
                    old_src = old_src.substring(0, n != -1 ? n : old_src.length);
                    var new_src = old_src + '?' + d.getTime();
                    console.log(new_src);
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
         $ul = $('.comments ul');
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
        var
         _this = this;
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
        $ul = $('.comments ul'),
        val = $textarea.val();
        if (val.length < 1)
            return;
        $.ajax({
            url: LionFace.User['images_comments_ajax'],
            type: 'POST',
            data: {
                'method': 'create',
                'message': val,
                'pk': $ul.data('image-pk')
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
                    // follow image
                    $('.image_popup').find('#add_post_follower:visible').click();
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
        $ul = $('.comments ul');
        $ul.data('image-pk', $item.data('pk'));
        $.ajax({
            url: LionFace.User['images_comments_ajax'],
            data: {
                'method': 'list',
                'pk': $ul.data('image-pk')
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
            $ul = $('.image_popup .comments ul');

        $.ajax({
            url: LionFace.User['images_comments_ajax'],
            type: 'POST',
            data: {
                'method': 'delete',
                'comment_pk': $item.data('pk'),
                'pk': $ul.data('image-pk')
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
        var id = $this.attr('id');
        var url = $this.attr('href');
        var post = $('.image_container');
        var item = post.find('li[popup=true]');
        var followings = item.data('following');
        var loves_count = parseInt(item.data('loves'));
        var data = {
            'user': LionFace.User.username,
            'imagepk': item.data('pk')
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
                        loves_count = loves_count - 1;
                        $('.image_popup').find('.loves_count').html(loves_count);
                        if (loves_count == 0) {
                            $('.image_popup').find('.loves_count').hide();
                        }
                        $('.image_popup').find('#rem_post_lovers').hide();
                        $('.image_popup').find('#add_post_lovers').show();
                    }
                    else {
                        followings.push(LionFace.User.username);
                        loves_count = loves_count + 1;
                        $('.image_popup').find('.loves_count').html(loves_count);
                        $('.image_popup').find('#add_post_lovers').hide();
                        $('.image_popup').find('#rem_post_lovers').show();
                        $('.image_popup').find('.loves_count').show();
                    }
                    item.data('lovers',followings)
                    item.data('loves',loves_count)
                }
            }
        });
    },

    post_followers: function(e, el) {
        e.preventDefault();
        var _this = this;
        var $this = el;
        var id = $this.attr('id');
        var url = $this.attr('href');
        var post = $('.image_container');
        var item = post.find('li[popup=true]');
        var followings = item.data('following');
        var data = {
            'user': LionFace.User.username,
            'imagepk': item.data('pk')
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
                        $('.image_popup').find('#rem_post_follower').hide();
                        $('.image_popup').find('#add_post_follower').show();
                    }
                    else {
                        followings.push(LionFace.User.username);
                        $('.image_popup').find('#add_post_follower').hide();
                        $('.image_popup').find('#rem_post_follower').show();
                    }
                    item.data('following',followings)
                }
            }
        });
    },

    bind_popup: function() {
        var _this = this;
        var $popup = $('.image_popup');
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
        $popup.find('.image_zone_view').mousemove(
            function(event) {
                $(this).find('.rotate-left, .rotate-right').find('img').fadeIn(_this.options.popup_fadeDuration);
            }
        ).mouseleave(
            function(event) {
                $(this).find('.rotate-left, .rotate-right').find('img').fadeOut(_this.options.popup_fadeDuration);
            } 
        );
        $(document).on('mouseenter', '.image_album', function() {
                $(this).siblings('#image_settings').show();
            });
        $(document).on('mouseleave', '.album_shadow', function() {
                $(this).find('#image_settings').hide();
            }
        );
        $popup.find('.image_zone_view .rotate-left').click(function(event) {
            _this.rotate_image_left();
        });
        $popup.find('.image_zone_view .rotate-right').click(function(event) {
            _this.rotate_image_right();
        });
        $popup.find('.image_zone_view .prev').click(function(event) {
            _this.popup_to_prev();
        });
        $popup.find('.image_zone_view .next').click(function(event) {
            _this.popup_to_next();
        });
        $popup.find('.post_followers').click(function(e) {
            _this.post_followers(e, $(this));
        });
        $popup.find('.post_lovers').click(function(e) {
            _this.post_lovers(e, $(this));
        });
        this.popup_comments_bind_make_comment();
    },

    load_quote: function () {
        var url = LionFace.User['images_quote_ajax'],
            $reset_quote = $('#reset-quote');

        $reset_quote.hide();
        $('#image_quote').hover(function () {
            if (!$reset_quote.hasClass('default')) {
                $reset_quote.show();
            }
        }, function () {
            if (!$reset_quote.hasClass('default')) {
                $reset_quote.hide();
            }
        });

        var set_quote = function(data) {
            if (data.success == 'true') {
                $('#quote').text(data.quote);
                $('#author').text(data.author);
                if (data.default_quote == 'true') {
                    $reset_quote.addClass('default');
                    $reset_quote.hide();
                }
            }
        };
        $reset_quote.click(function () {
            var data = {
                method: 'reset'
            };
            make_request({
                url: url,
                data: data,
                callback: function (data) {
                    set_quote(data);
                }
            });
            return false;
        });
        make_request({
            url: url,
            data: {method: 'get'},
            callback: function (data) {
                set_quote(data);
            }
        });

        var post_quote_change = function () {
            var quote = $('#quote').text(),
                author = $('#author').text(),
                data = {
                    method: 'change',
                    change: {
                        quote: quote,
                        author: author
                    }
                };
            make_request({
                url: url,
                data: data,
                callback: function (data) {
                    if (data.default_quote == 'false') {
                        $reset_quote.removeClass('default');
                    }
                }
            });
        };

        var $quote = $('#quote, #author');
        $quote.hover(function () {
            if ($(this).prop('contenteditable') == 'true') {
                $(this).addClass('editable');
                $(this).css('margin', -1);
            }
        }, function () {
            if ($(this).prop('contenteditable') == 'true') {
                $(this).removeClass('editable');
                $(this).css('margin', 0);
            }
        });
        $quote.keypress(function (e) {
            if (e.which == 13) {
                $(this).blur();
                return false;
            }
        });
        $('#quote').keypress(function (e) {
            if ($(this).text().length > 69) {
                return false;
            }
            if (e.which == 9) {
                $('#author').focus();
            }
        });
        $('#author').keypress(function() {
            if ($(this).text().length > 19) {
                return false;
            }
        });
        $quote.focusout(function () {
            post_quote_change();
        });
    }
};

$(function() {
    LionFace.Images = new LionFace.Images();
});
