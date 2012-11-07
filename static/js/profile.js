LionFace.Profile = function() {
    this.runner();
}


LionFace.Profile.prototype = {

    runner : function() {
        if (!LionFace.User.is_anonymous) {
            this.bind_upload_form();
            this.bind_postbox();
            this.bind_albums();
            this.bind_profile_pictures();
            this.bind_love_list();
        }

    },

    //restrict image size and format before upload
    bind_upload_form : function() {
        $('#id_photo').bind('change', function() {
                console.log(this.files[0].type);
                console.log(this.files[0].size);
                if(this.files[0].size > 1048576) {
                    $('#submit_img_btn').hide();
                    if ($('.errorlist').length) {
                        $('.errorlist').html('<li>Image file too large ( &gt; 1mb )</li>');
                    }
                    else {
                        $('.upload_form').prepend('<ul class="errorlist"><li>Image file too large ( &gt; 1mb )</li></ul>');
                    }
                } 
                else if(this.files[0].type == 'image/gif') {
                    $('#submit_img_btn').hide();
                    if ($('.errorlist').length) {
                        $('.errorlist').html('<li>Gif images are not allowed</li>');
                    }
                    else {
                        $('.upload_form').prepend('<ul class="errorlist"><li>Gif images are not allowed</li></ul>');
                    }      
                }
                else if(this.files[0].type.indexOf("image") == -1) {
                    $('#submit_img_btn').hide();
                    if ($('.errorlist').length) {
                        $('.errorlist').html('<li>Please upload a valid image</li>');
                    }
                    else {
                        $('.upload_form').prepend('<ul class="errorlist"><li>Please upload a valid image</li></ul>');
                    }      
                }       
                else{
                    $('#submit_img_btn').show();
                    $('.errorlist').html(''); 
                }
            });

        $("#upload_picture").click(function(event){
          event.stopPropagation();
          $('.upload_form').show(); 
        });  

        $("#reset_picture").click(function(event){
          event.stopPropagation();
        });

        $("#send_message").click(function(event){
          event.stopPropagation();
          $('.send_message_form').show(); 
        });

        $('.noPhoto').hover(
                function(){$('.upload').show();},
                function(){$('.upload').hide();}
        );
    },

    bind_postbox : function() {

        $("#postbox .postcontent").focus(function() {
            //$("#postbox .postoptions").slideDown();
            if($(this).val() == 'Share something...') {
                $(this).val("");
            }
        });
        $("#postbox .postcontent").focusout(function() {
            //$("#postbox .postoptions").slideUp();
            if($(this).val() == '') {
                $(this).val("Share something...");
            }
        });


        $("#postboxbutton").click(function() {
            var url = '/posts/save/'
            make_request({
                url:url,
                data: $('#postform').serialize(), 
                callback: function(data) {
                        $("#news_feed").prepend(data.html);
                        $('.postbox_textarea').val('');
                        console.log('saving');
                        make_excerpts();
                },
            });
            return false;
        });

        $(document).on('click','.post_option',function(){
            $(this).find('input').prop('checked', true);
        });

    /*
    //Submit on enter

        $('.postcontent').keypress(function(e){
            if(e.which == 13){
                $.ajax({
                    url: url,
                    data: $('#postform').serialize(),
                    type: 'POST',
                    dataType: 'json',
                    success: function(data) {
                        //$("#postbox .postcontent").val("");
                        $("#news_feed").prepend(data.html);
                        $('.postbox_textarea').val('');
                    },
                    error: function() {
                        alert("Failed to save new post.  Please try again later.");
                    }
                });

                return false;   
            }
        });
    */

        $('.postbox_textarea').autosize();

    },

    bind_albums : function() {
    /*********** Albums ***********/
        var self_class = this;

        /** Create album */
        $(document).on('submit','#create_album_form',function(e) {    
            e.preventDefault();
            var albums = parseInt(LionFace.User.album_count);
            var url = 'album_create/';
            make_request({
                url:url,
                data:$(this).serialize(),
                callback:function(data){
                    if (data.status == 'OK' && data.html) {
                        $('.albums').append(data.html);
                        $('#album_name').val('');
                        $('.albums').show();
                        albums = albums + 1;
                        LionFace.User.album_count = albums;
                        self_class.hide_album_hint();
                    }
                },
                errorback:function(){
                }
            });

        });

        /** Delete album */
        $(document).on('click','.albums_edit',function(e) {    
            var self = $(this);
            var url = 'delete_album/';
            var albums = parseInt(LionFace.User.album_count);
            var album_id = get_int(self.parent().attr('id'));
            make_request({
                url:url,
                data:{
                    album_id:album_id,    
                },
                callback:function(data){
                    if (data.status == 'OK') {
                        self.parent().slideUp();
                        albums = albums - 1;
                        LionFace.User.album_count = albums;
                        self_class.hide_album_hint();
                    }
                },
            });

        });       

        /** Show create form */
        $(document).on('click','#create_album_link',function(e) {    
            var toggled = $(this).data('toggled');
            $(this).data('toggled', !toggled);     
            if (!toggled){
                $('#create_album_form').show();
                $('#album_name').focus();
            }
            else {
                $('#create_album_form').hide();
            }
        });

        /** inline name change */
        $(document).on('click','.album_name_list',function(e) {
            var self = $(this);
            var album_id = get_int(self.parent().attr('id'));
            var name = $(this).html();
            self.replaceWith('<input id="edit_album_name" name="album_name">');
            $('#edit_album_name').focus();
            $('#edit_album_name').blur(function() {
                var new_name = $(this).val(); 
                if (new_name == '' || new_name == name) {
                    $(this).replaceWith(self);
                }else {
                    var url = 'album_name/' 
                    make_request({
                        url:url,
                        data:{
                            album_id:album_id,
                            album_name:new_name
                        },
                        callback:function(data){
                            if (data.status =='OK') {
                                self.html(new_name);
                            }
                        }
                    })
                    $(this).replaceWith(self);
                }
            });
        });

        // Making sortable
        var pos_bgn = 0;

        $( ".albums, .sortable" ).sortable({
            start: function(event, ui) { 
                pos_bgn = ui.item.index();
            },
            stop: function(event, ui) {
                /*console.log("New position: " + ui.item.index());*/
                /*console.log("Old position: " + pos_bgn);*/
                var item_id = get_int(ui.item[0].id)
                url = 'change_position/'
                if (ui.item.index() != pos_bgn) {
                    make_request({
                        url:url,
                        data: {
                            album_id:item_id,
                            position_bgn:pos_bgn,
                            position_end:ui.item.index()
                        },
                        callback: function() {
                        }
                    });
                }
            }
        });
        $( ".albums, .sortable" ).disableSelection();
    },

    set_backgroundImage: function(backgroundImage) {
        if (backgroundImage == undefined)
            return false;
        /** Set thumb as backgroundImage for all div elements have attr thumb */
        $('div[thumb]').each(function(index, elem) {
            $(elem).animate({
                'opacity': 0,
            }, 1000, '', function() {
                $(this).css({
                    'backgroundImage': backgroundImage,
                }).animate({
                    'opacity': 1,
                }, 1000);
            });
        });
    },
    
    swap_images: function(li1, li2, delay) {
        if (li1 == undefined || li2 == undefined)
            return false;
        if ( delay == undefined )
            delay = 1000;
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
        var swap_images = this.swap_images;
        function swap(elem1, elem2) {
            swap_images(elem1, elem2, 0);
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

    bind_profile_pictures : function() {
        /** Connect drag+drop for manual sorting */
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
                        LionFace.Profile.swap_images(item2, $('.image_container li').get(1), 0);
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
                                LionFace.Profile.set_positions_images( data.positions );
                            } else {
                                LionFace.Profile.sort_images();
                            }
                        },
                        error: function(jqXHR, textStatus, errorThrown) {
                            console.log( '1' );
                            LionFace.Profile.sort_images();
                        },
                    });
                }
            },
        });
        $('.image_container ul').disableSelection();
        /** Init actions on image */
        function image_setting(index, elem) {
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
            /** Make primary photo **/
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
                            $(li1).find('#make_primary').show();
                            if ( !$(li1).is($(li2)) ) {
                                $(li2).find('#make_primary').attr('activity', '0');
                                $(li2).find('#make_primary').hide();
                            }
                            LionFace.Profile.set_positions_images( data.positions, false );
                            LionFace.Profile.swap_images(li1, li2).then(function() {
                                LionFace.Profile.sort_images();
                            });
                            LionFace.Profile.set_backgroundImage( data.backgroundImage );
                        } else if ( data.status == 'fail' ) {
                            /**  */
                        }
                    },
                });
                return false;
            });
            /** Delete photo */
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
                            LionFace.Profile.set_backgroundImage( data.backgroundImage );
                            var li = $(image_settings).parent().parent();
                            var ul = $(li).parent();
                            $(ul).animate({
                                'opacity': 0,
                            }, 500, '', function() {
                                $(li).remove();
                                if ( data.html != undefined ) {
                                    var item = $(data.html).filter('li');
                                    if ( $(item).attr('pk') != $(ul).find('li:last').attr('pk') ) {
                                        image_setting(undefined, $(item));
                                        $(ul).find('li:last').after( $(item) );
                                    }
                                }
                                LionFace.Profile.set_positions_images( data.positions );
                                $(ul).animate({
                                    'opacity': 1,
                                }, 500);
                            });
                        } else if ( data.status == 'fail' ) {
                            /**  */
                        }
                    },
                });
                return false;
            });
        }
        this.sort_images();
        $('.image_container li').each(image_setting);
        /** View more button */
        if ( LionFace.User['profile_images_now_rows'] < LionFace.User['profile_images_total_rows'] ) {
            var view_more = $('.image_container .view_more');
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
                            $(items).each(image_setting);
                            $(items).each(function(index, elem) {
                                $(elem).css({'opacity': 0});
                            });
                            $('.image_container li:last').after( $(items) );
                            $(items).each(function(index, elem) {
                                $(elem).animate({'opacity': 1}, 1000);
                            });
                            LionFace.Profile.set_positions_images(data.positions);
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

    hide_album_hint : function() {
        if ($('#albums_hint').length && parseInt(LionFace.User.album_count) < 2) {
            $('#albums_hint').hide();
        }
        else {
            $('#albums_hint').show();
        }
    },

    bind_love_list : function() {
        // multiple filters for loves
        $(document).on('click', '.loving', function(){
            $(this).toggleClass('filterON');
            $(this).toggleClass('filter');

            params = [];

            $('.filterON').each(function () {
                params.push("&"+$(this).attr('id'));
            });
            if (params) {
                params = "?"+params.join("").slice(1)+"&ajax";
                if (params == "?&ajax") {
                    params = [];
                }
            }
            var url = params;
            if (params.length) {
                make_request({
                    url:url, 
                    callback:function (data) {
                        if (data.html) {
                            $('#result_table').html(data.html);
                        }
                    }
                });
            }
            else {
                $('#result_table').html(''); 
            }

        });   
    },

}

$(function() {         
    LionFace.Profile = new LionFace.Profile();
    LionFace.Profile.hide_album_hint();
});
