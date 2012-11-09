LionFace.Images = function() {
    this.init();
}

LionFace.Images.prototype = {

    options: {
        swap_images_default_delay: 1000,
        set_backgroundImage_default_delay: 1000,
        overlay_fadeDuration: 500,
    },

    init: function() {
        var _this = this;
        $('.image_container li').each(function(index, elem) {
            _this.create_settings(elem);
        });
        _this.sort_images();
        _this.bind_view_more_button();
        if (!LionFace.User.is_anonymous) {
            _this.bind_sorting();
        }
        $('#image_overlay').click(function() {
            _this.popup_end();
            return false;
        });
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
            a = parseInt($(a).attr('position'));
            b = parseInt($(b).attr('position'));
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
            $(elem).attr('position', data[$(elem).attr('pk')]);
        });
        if (resort)
            this.sort_images();
    },

    create_settings: function(elem) {
        var _this = this;
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
        ).click(function() {
            _this.popup_start($(this));
            return false;
        });
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
                    'pk': $(image_settings).parent().parent().attr('pk'),
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
                    'pk': $(image_settings).parent().parent().attr('pk'),
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
                                if ( $(item).attr('pk') != $(ul).find('li:last').attr('pk') ) {
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

    popup_sizeOverlay: function() {
        return $('#image_overlay').width($(document).width()).height($(document).height());
    },

    popup_start: function(elem) {
        $(window).on("resize", this.popup_sizeOverlay);
        $('select, object, embed').css({
            visibility: "hidden"
        });
        $('#image_overlay').width($(document).width()).height($(document).height()).fadeIn(this.options.overlay_fadeDuration);
        
    },

    popup_end: function() {
        $(window).off("resize", this.popup_sizeOverlay);
        $('#image_overlay').fadeOut(this.options.overlay_fadeDuration);
        $('select, object, embed').css({
            visibility: "visible"
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
                            'pk': $(item2).attr('pk'),
                            'instead': $(item1).attr('pk'),
                        },
                        success: function(data, textStatus, jqXHR) {
                            if (data.status == 'ok') {
                                _this.set_positions_images( data.positions );
                            } else {
                                _this.sort_images();
                            }
                        },
                        error: function(jqXHR, textStatus, errorThrown) {
                            console.log( '1' );
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
    LionFace.Images = new LionFace.Images();
});