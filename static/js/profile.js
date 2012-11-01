LionFace.Profile = function() {
    this.runner();
}


LionFace.Profile.prototype = {

    runner : function() {
        if (!LionFace.User.is_anonymous) {
            this.bind_upload_form();
            this.bind_postbox();
            this.bind_albums();
            this.bind_image_container();
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

        $( ".sortable" ).sortable({
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
        $( ".sortable" ).disableSelection();
    },

    bind_image_container : function() {
        $('div.image_container td').each(function(index, elem) {
            $(elem).find('div:first').hover(
                function () {
                    $(this).find('#image_settings').show();
                },
                function () {
                    $(this).find('#image_settings').hide();
                }
            );
        });
        //alert(LionFace.Profile.link);
        $('div.image_container div.view_more a').click(function() {
            
        });
    },

    hide_album_hint : function() {
        if ($('#albums_hint').length && parseInt(LionFace.User.album_count) < 2) {
            $('#albums_hint').hide();
        }
        else {
            $('#albums_hint').show();
        }
    },

}

$(function() {         
    LionFace.Profile = new LionFace.Profile();
    LionFace.Profile.hide_album_hint();
});
