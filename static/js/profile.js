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
                if(this.files[0].size > 1000141) {
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
        var post_bgn = 0;

        $( ".albums, .sortable" ).sortable({
            start: function(event, ui) { 
                post_bgn = ui.item.index();
            },
            stop: function(event, ui) {
                /*console.log("New position: " + ui.item.index());*/
                /*console.log("Old position: " + post_bgn);*/
                var item_id = get_int(ui.item[0].id)
                url = 'change_position/'
                if (ui.item.index() != post_bgn) {
                    make_request({
                        url:url,
                        data: {
                            album_id:item_id,
                            position_bgn:post_bgn,
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

    bind_profile_pictures : function() {
        $( "div.image_container table" ).sortable({
            items: 'td',
            start: function(event, ui) {
                
            },
        }).disableSelection();
        /** Function for init actions on image */
        function image_setting(index, elem) {
            var image_settings = $(elem).find('div:first #image_settings');
            if ( $(image_settings).length == 1 ) {
                $(image_settings).hide();
                $(elem).find('div:first').hover(
                    function() {
                        $(image_settings).show();
                    },
                    function() {
                        $(image_settings).hide();
                    }
                );
                /** Make primary photo */
                $(image_settings).find('#make_primary').click(function() {
                    $.ajax({
                        url: LionFace.User['profile_images_url_primary'],
                        type: 'POST',
                        data: {
                            'pk': $(image_settings).attr('pk'),
                        },
                        success: function(data, textStatus, jqXHR) {
                            if ( data.status == 'ok' ) {
                                if ( data.backgroundImage != undefined )
                                    LionFace.Profile.set_backgroundImage( data.backgroundImage );
                                /** Exchange first image and new photo */
                                var td1 = $(image_settings).parent().parent();
                                var td2 = $('div.image_container td:first');
                                if ( !$(td1).is($(td2)) ) {
                                    var ntd1 = $(td1).clone().css({
                                        'opacity': 0,
                                    });
                                    var ntd2 = $(td2).clone().css({
                                        'opacity': 0,
                                    });
                                    $(td1).animate({
                                        'opacity': 0,
                                    }, 1000);
                                    $(td2).animate({
                                        'opacity': 0,
                                    }, 1000);
                                    /** After hided tds, we change their */
                                    setTimeout(function() {
                                        $(td2).after( $(ntd1) );
                                        $(td1).after( $(ntd2) );
                                        $(td1).remove();
                                        $(td2).remove();
                                        image_setting(undefined, $(ntd1));
                                        image_setting(undefined,  $(ntd2));
                                        /** And show their */
                                        $(ntd1).animate({
                                            'opacity': 1,
                                        }, 1000);
                                        $(ntd2).animate({
                                            'opacity': 1,
                                        }, 1000);
                                    }, 1000);
                                }
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
                            'pk': $(image_settings).attr('pk'),
                            'row': LionFace.User['profile_images_now_rows'],
                        },
                        success: function(data, textStatus, jqXHR) {
                            if ( data.status == 'ok' ) {
                                /** Now we delete current image and shift all images */
                                var tr = $(image_settings).parent().parent().parent();
                                $(tr).parent().animate({
                                    'opacity': 0,
                                }, 500);
                                setTimeout(function() {
                                    $(image_settings).parent().parent().remove();
                                    while ( true ) {
                                        ntr = $(tr).next();
                                        if ( $(ntr).next().prop('tagName') == undefined ) {
                                            if ( data.html != undefined ) {
                                                var item = $(data.html).find('td:first');
                                                if ( $(item).length == 1 ) {
                                                    var td = $(tr).find('td:last');
                                                    if ( $(td).length == 0 && $(tr).prev().prop('tagName') != undefined) {
                                                        td = $(tr).prev().find('td:last');
                                                    }
                                                    if ( $(td).length == 0 || $(td).html() != $(item).html() ) {
                                                        image_setting(undefined, $(item));
                                                        $(tr).find('td:last').after( $(item) );
                                                    }
                                                }
                                            }
                                            break;
                                        }
                                        $(tr).find('td:last').after( $(ntr).find('td:first') );
                                        tr = ntr;
                                    }
                                    $(tr).parent().animate({
                                        'opacity': 1,
                                    }, 500);
                                }, 500);
                                /** Change number of photos */
                                if ( data.photos_count != undefined )
                                    $('#photos_count').html( data.photos_count );
                                /** Change primary photo */
                                if ( data.backgroundImage != undefined )
                                    LionFace.Profile.set_backgroundImage( data.backgroundImage );
                            } else if ( data.status == 'fail' ) {
                                /**  */
                            }
                        },
                    });
                    return false;
                });
            }
        }
        $('div.image_container td').each(image_setting);
        /** View more button */
        if ( LionFace.User['profile_images_now_rows'] < LionFace.User['profile_images_total_rows'] ) {
            var view_more = $('div.image_container div.view_more');
            $(view_more).show();
            $(view_more).find('a').click(function() {
                /** XHR request for show more pictures */
                $.ajax({
                    url: LionFace.User['profile_images_url_more'],
                    type: 'POST',
                    data: {
                        'row': LionFace.User['profile_images_now_rows'] + 1,
                    },
                    beforeSend: function(jqXHR, settings) {
                        $(view_more).find('div.view_more_loader').show(250);
                    },
                    success: function(data, textStatus, jqXHR) {
                        if ( data.status == 'ok' ) {
                            LionFace.User['profile_images_now_rows']++;
                            LionFace.User['profile_images_total_rows'] = data.total_rows;
                            if ( LionFace.User['profile_images_now_rows'] >= LionFace.User['profile_images_total_rows'] ) {
                                $(view_more).hide(500);
                            }
                            var item = $(data.html);
                            $(item).find('td').each(image_setting);
                            $(item).insertBefore($('div.image_container tr:last'));
                        }
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        $(view_more).prepend('<div class="error" style="font-size: 20px;">' + errorThrown + '</div>');
                        setTimeout(function() {
                            setTimeout(function() {
                                $(view_more).find('div.error').remove();
                            }, 500);
                            $(view_more).find('div.error').hide(500);
                        }, 5000);
                    },
                    complete: function(jqXHR, textStatus) {
                        $(view_more).find('div.view_more_loader').hide(500);
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
