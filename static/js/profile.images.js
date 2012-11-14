LionFace.ProfileImages = function() {
    this.init();
}

LionFace.ProfileImages.prototype = {

    options: {
        'swap_images_default_delay': 1000,
        'set_backgroundImage_default_delay': 1000,
        'popup_fadeDuration': 500,
    },

    init: function() {
        var _this = this;
        $('.image_container li').each(function(index, elem) {
            _this.create_settings(elem);
        });
        this.sort_images();
        if (!LionFace.User.is_anonymous) {
            this.bind_sorting();
        }
        this.bind_view_more_button();
        this.bind_popup();
    },

    set_backgroundImage: function(backgroundImage) {
        if (backgroundImage == undefined)
            return false;
        var _this = this;
        $('div[thumb]').each(function(index, elem) {
            $(elem).animate({
                'opacity': 0,
            }, _this.set_backgroundImage_default_delay, '', function() {
                $(this).css({
                    'backgroundImage': backgroundImage,
                }).animate({
                    'opacity': 1,
                }, _this.set_backgroundImage_default_delay);
            });
        });
    },

    swap_images: function(li1, li2, delay) {
        if (li1 == undefined || li2 == undefined)
            return false;
        if ( delay == undefined )
            delay = this.options.swap_images_default_delay;
        var d = $.Deferred();
        if (delay == 0) {
            if ( !$(li1).is($(li2)) ) {
                var point = $('<span></span>').hide();
                $(li1).after( $(point) );
                $(li2).after( $(li1) );
                $(point).after( $(li2) );
                $(point).remove();
            }
            d.resolve();
        } else {
            if ( $(li1).is($(li2)) ) {
                $(li1).animate({
                    'opacity': 0,
                }, delay, '', function() {
                    $(li1).animate({
                        'opacity': 1,
                    }, delay, '', function() {
                        d.resolve();
                    });
                });
            } else {
                var ds = new Array();
                for (var i = 0; i < 4; ++i)
                    ds.push($.Deferred());
                $(li1).animate({
                    'opacity': 0,
                }, delay, '', function() {
                    ds[0].resolve();
                });
                $(li2).animate({
                    'opacity': 0,
                }, delay, '', function() {
                    ds[1].resolve();
                });
                $.when(ds[0], ds[1]).then(function() {
                    var point = $('<span></span>').hide();
                    $(li1).after( $(point) );
                    $(li2).after( $(li1) );
                    $(point).after( $(li2) );
                    $(point).remove();
                    $(li1).animate({
                        'opacity': 1,
                    }, delay, '', function() {
                        ds[2].resolve();
                    });
                    $(li2).animate({
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

    sort_images: function() {
        var selector = '.image_container li';
        var _this = this;
        function swap(elem1, elem2) {
            _this.swap_images(elem1, elem2, 0);
        }
        function cmp_images(a, b) {
            a = parseInt($(a).data('position'));
            b = parseInt($(b).data('position'));
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
        if (data == undefined)
            return false;
        if (resort == undefined)
            resort = true;
        $('.image_container li').each(function(index, elem) {
            $(elem).data('position', data[$(elem).data('pk')]);
        });
        if (resort)
            this.sort_images();
    },

    create_settings: function(elem) {
        var _this = this;
        $(elem).click(function() {
            $(this).attr('popup', true);
            _this.popup_start(elem);
            return false;
        });
        var image_settings = $(elem).find('#image_settings');
        if ( $(image_settings).length != 1 )
            return;
        $(image_settings).hide();
        $(elem).find('.image_album').hover(
            function() {
                $(image_settings).show();
            },
            function() {
                $(image_settings).hide();
            }
        );
        if ( $(image_settings).find('#make_primary').attr('activity') == 1) {
            $(image_settings).find('#make_primary').hide();
        } else {
            $(image_settings).find('#make_primary').show();
        }
        $(image_settings).find('#make_primary').click(function() {
            $.ajax({
                url: LionFace.User['profile_images_url_primary'],
                type: 'POST',
                data: {
                    'pk': $(image_settings).parent().parent().data('pk'),
                },
                success: function(data, textStatus, jqXHR) {
                    if ( data.status == 'ok' ) {
                        var li1 = $(image_settings).parent().parent();
                        var li2 = $('.image_container li:first');
                        $(li1).find('#make_primary').attr('activity', '1');
                        $(li1).find('#make_primary').hide();
                        if ( !$(li1).is($(li2)) ) {
                            $(li2).find('#make_primary').attr('activity', '0');
                            $(li2).find('#make_primary').show();
                        }
                        _this.set_positions_images( data.positions, false );
                        _this.swap_images(li1, li2).then(function() {
                            _this.sort_images();
                        });
                        _this.set_backgroundImage( data.backgroundImage );
                    } else if ( data.status == 'fail' ) {
                        
                    }
                },
            });
            return false;
        });
        $(image_settings).find('#delete').click(function() {
            $.ajax({
                url: LionFace.User['profile_images_url_delete'],
                type: 'POST',
                data: {
                    'pk': $(image_settings).parent().parent().data('pk'),
                    'row': LionFace.User['profile_images_now_rows'],
                },
                success: function(data, textStatus, jqXHR) {
                    if ( data.status == 'ok' ) {
                        if ( data.photos_count != undefined )
                            $('#photos_count').html( data.photos_count );
                        _this.set_backgroundImage( data.backgroundImage );
                        var li = $(image_settings).parent().parent();
                        var ul = $(li).parent();
                        $(ul).animate({
                            'opacity': 0,
                        }, 500, '', function() {
                            $(li).remove();
                            if ( data.html != undefined ) {
                                var item = $(data.html).filter('li');
                                if ( $(item).data('pk') != $(ul).find('li:last').data('pk') ) {
                                    _this.create_settings($(item));
                                    $(ul).find('li:last').after( $(item) );
                                }
                            }
                            _this.set_positions_images( data.positions );
                            $(ul).animate({
                                'opacity': 1,
                            }, 500);
                        });
                    } else if ( data.status == 'fail' ) {
                        
                    }
                },
            });
            return false;
        });
    },

    popup_enableKeyboard: function() {
        var _this = this;
        function keyboard(event) {
            var KEYCODE_ESC = 27;
            var KEYCODE_LEFTARROW = 37;
            var KEYCODE_RIGHTARROW = 39;
            var keycode = event.keyCode;
            var key = String.fromCharCode(keycode).toLowerCase();
            if (keycode === KEYCODE_ESC) {
                _this.popup_end();
            } else if (key === 'p' || keycode === KEYCODE_LEFTARROW) {
                _this.popup_to_prev();
            } else if (key === 'n' || keycode === KEYCODE_RIGHTARROW) {
                _this.popup_to_next();
            }
        }
        $(document).on('keyup.keyboard', keyboard);
    },

    popup_disableKeyboard: function() {
        $(document).off('.keyboard');
    },

    popup_resize: function() {
        $('.image_popup').css({
            top: $(window).scrollTop() + 'px',
            left: $(window).scrollLeft() + 'px'
        });
        $('.image_zone_view').width($('.image_zone').width() - 351);
        $('.image_zone_view').find('.prev, .next').css({
            'width': $('.image_zone').width()*0.2 + 'px',
        }).find('img').css({
            'margin-top': ($('.image_zone').height()-45)/2,
        });
        $('.image_zone_view .next').css({
            'margin-left': $('.image_zone').width()*(1 - 0.2) - 351,
        });
        $('.image_zone_view .loader').css({
            'line-height': $('.image_zone').height() + 'px',
        });
        $('.image_zone_info .scroll_area').height(
            $('.image_zone_info').height()
            - $('.image_zone_info .close').height()
            - $('.image_zone_info .make_comment').height()
            - 15
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
                "height": newHeight + "px",
            }).attr({
                "width": newWidth,
                "height": newHeight
            });
        }
        $(image).css({
            'margin-top': ($('.image_zone_view').height() - $(image).height()) / 2,
        });
        return false;
    },

    popup_to_prev: function() {
        var now = $('.image_container li[popup=true]');
        var next = undefined;
        if ($('.image_container li').length > 1) {
            if ($(now).prev().length > 0) {
                next = $(now).prev();
            } else {
                next = $('.image_container li:last');
            }
        }
        this.popup_change_item($(next));
    },

    popup_to_next: function() {
        var now = $('.image_container li[popup=true]');
        var next = undefined;
        if ($('.image_container li').length > 1) {
            if ($(now).next().length > 0) {
                next = $(now).next();
            } else {
                next = $('.image_container li:first');
            }
        }
        this.popup_change_item($(next));
    },

    popup_change_item: function(item, change) {
        if (item == undefined)
            return false;
        if (change == undefined)
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
            $('.image_zone_info .make_comment').show();
            _this.popup_resize();
        });
        $('.image_zone_view .image').append( $(image) );
        $(image).attr('src', $(item).find('div.image_album').attr('data-original-url'));
        // load comments
        var $ul = $('.image_zone_info .comments ul');
        $.ajax({
            url: LionFace.User['profile_image_comments_part'],
            data: {
                'pk': $(item).data('pk'),
            },
            beforeSend: function(jqXHR, settings) {
                $ul.hide().html('');
            },
            success: function(data, textStatus, jqXHR) {
                if (data.status == 'ok') {
                    $(data.comments).filter('li').each(function(index, elem) {
                        $ul.append($(elem));
                    });
                    $ul.fadeIn(200);
                } else {
                    this.error(jqXHR, textStatus);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                
            },
        });
        // make comment
        $('.image_zone_info .make_comment').hide();
        if (change) {
            $('.image_zone_info .make_comment textarea').val('');
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
        $('.image_popup .image_zone, .image_popup .image_info').hide();
        $('.image_popup').fadeOut(this.options.popup_fadeDuration);
        this.popup_disableKeyboard();
        $('body').css({'overflow': this.popup_start.overflow});
        this.popup_start.overflow = undefined;
    },

    bind_popup: function() {
        var _this = this;
        $('.image_overlay').click(function() {
            _this.popup_end();
            return false;
        });
        $('.image_zone_info .close a').click(function() {
            _this.popup_end();
            return false;
        });
        $(window).on('resize', this.popup_resize);
        $(document).on('resize', this.popup_resize);
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
        // textarea in make_comment
        $('.image_zone_info .make_comment textarea').autosize({
            callback: function(ta) {
                _this.popup_resize();
            },
        }).keydown(function(event){
            var
            KEYCODE_ENTER = 13,
            keycode = event.keyCode;
            if (keycode == KEYCODE_ENTER) {
                var
                $this = $(this),
                val = $this.val();
                if (val.length > 1) {
                    $.ajax({
                        url: LionFace.User['profile_images_comments_create'],
                        type: 'POST',
                        data: {
                            'comment': val,
                            'pk': $('.image_container li[popup=true]').data('pk'),
                        },
                        beforeSend: function(jqXHR, settings) {
                            $this.data('val', val);
                            $this.val(' ');
                            $this.prop('disabled', true);
                        },
                        success: function(data, textStatus, jqXHR) {
                            if (data.status == 'ok') {
                                $this.val('');
                                
                            } else {
                                this.error(jqXHR, textStatus);
                            }
                        },
                        error: function(jqXHR, textStatus, errorThrown) {
                            $this.val($this.data('val'));
                        },
                        complete: function(jqXHR, textStatus) {
                            $this.prop('disabled', false);
                        },
                    });
                }
                return false;
            }
        });
    },

    bind_sorting: function() {
        var _this = this;
        var pos_bgn;
        $('.image_container ul').sortable({
            start: function(event, ui) {
                pos_bgn = ui.item.index();
            },
            stop: function(event, ui) {
                if ( pos_bgn == ui.item.index() )
                    return;
                var pos_end = ui.item.index();
                var item1 = $('.image_container li').get( pos_bgn );
                var item2 = $('.image_container li').get( pos_end );
                if ( (pos_bgn == 0 && $(item2).find('#make_primary').attr('activity') == 1) ||
                     (pos_bgn == 1 && $(item1).find('#make_primary').attr('activity') == 1) ) {
                    $('.image_container ul').sortable('cancel');
                } else {
                    if ( pos_bgn >= 2 && pos_end == 0 &&
                         $($('.image_container li').get(1)).find('#make_primary').attr('activity') == 1 ) {
                        _this.swap_images(item2, $('.image_container li').get(1), 0);
                        pos_end = 1;
                        item2 = $('.image_container li').get( pos_end );
                    }
                    if (pos_bgn > pos_end)
                        item1 = $(item2).next();
                    if (pos_bgn < pos_end)
                        item1 = $(item2).prev();
                    $.ajax({
                        url: LionFace.User['profile_images_url_change_position'],
                        type: 'POST',
                        data: {
                            'pk': $(item2).data('pk'),
                            'instead': $(item1).data('pk'),
                        },
                        success: function(data, textStatus, jqXHR) {
                            if (data.status == 'ok') {
                                _this.set_positions_images( data.positions );
                            } else {
                                _this.sort_images();
                            }
                        },
                        error: function(jqXHR, textStatus, errorThrown) {
                            _this.sort_images();
                        },
                    });
                }
            },
        });
        $('.image_container ul').disableSelection();
    },

    bind_view_more_button: function() {
        var _this = this;
        var view_more = $('.image_container .view_more');
        if ( LionFace.User['profile_images_now_rows'] >= LionFace.User['profile_images_total_rows'] ) {
            $(view_more).hide();
        } else {
            $(view_more).show();
            $(view_more).find('a').click(function() {
                $.ajax({
                    url: LionFace.User['profile_images_url_more'],
                    type: 'POST',
                    data: {
                        'row': LionFace.User['profile_images_now_rows'],
                    },
                    beforeSend: function(jqXHR, settings) {
                        $(view_more).find('.view_more_loader').show(250);
                    },
                    success: function(data, textStatus, jqXHR) {
                        if ( data.status == 'ok' ) {
                            LionFace.User['profile_images_now_rows']++;
                            LionFace.User['profile_images_total_rows'] = data.total_rows;
                            if ( LionFace.User['profile_images_now_rows'] >= LionFace.User['profile_images_total_rows'] ) {
                                $(view_more).hide(500);
                            }
                            var items = $(data.html).filter('li');
                            $(items).each(function(index, elem) {
                                _this.create_settings(elem);
                            });
                            $(items).each(function(index, elem) {
                                $(elem).css({'opacity': 0});
                            });
                            $('.image_container li:last').after( $(items) );
                            $(items).each(function(index, elem) {
                                $(elem).animate({'opacity': 1}, 1000);
                            });
                            _this.set_positions_images(data.positions);
                        }
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        $(view_more).prepend('<div class="error" style="font-size: 20px;">' + errorThrown + '</div>');
                        setTimeout(function() {
                            setTimeout(function() {
                                $(view_more).find('.error').remove();
                            }, 500);
                            $(view_more).find('.error').hide(500);
                        }, 5000);
                    },
                    complete: function(jqXHR, textStatus) {
                        $(view_more).find('.view_more_loader').hide(500);
                    },
                });
                return false;
            });
        }
    },

}

$(function() {
    LionFace.ProfileImages = new LionFace.ProfileImages();
});
