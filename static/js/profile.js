var MAX_UPLOAD_IMAGES = 21;


LionFace.Profile = function() {
    this.runner();
};


LionFace.Profile.prototype = {

    runner : function() {
        if (!LionFace.User.is_anonymous) {
            this.bind_upload_form();
            this.bind_postbox();
            this.bind_albums();
            this.bind_love_list();
        }
        this.attach_image_count = 0;
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

        $(document).on('click','#upload_cover_profile', function(e) {
            e.stopPropagation();
            $('.upload_pforile_cover_form').show();
        });

        $('#upload_cancel').click(function(event) {
            $('.upload_form').fadeOut(function(){
                $('#id_image').val('');
            });
        });

        $(document).on('click','#cancel_cover_profile_btn', function(e) {
            $('.upload_pforile_cover_form').fadeOut();
        });

        $("#reset_profile_picture").click(function(event){
            event.stopPropagation();
        });

        /** restrict image cover uploads */
         $(document).on('change','#id_cover_photo',function() {
                if(this.files[0].size > 3145728) {  
                    $('#submit_cover_profile_btn').hide();
                    if ($('.errorlist').length) {
                        $('.errorlist').html('<li>Image file too large ( &gt; 3mb )</li>');
                    }
                    else {
                        $('.upload_pforile_cover_form').prepend('<ul class="errorlist"><li>Image file too large ( &gt; 3mb )</li></ul>');
                    } 
                }
                else if(this.files[0].type == 'image/gif') {
                    $('#submit_cover_profile_btn').hide();
                    if ($('.errorlist').length) {
                        $('.errorlist').html('<li>Gif images are not allowed</li>');
                    }
                    else {
                        $('.upload_pforile_cover_form').prepend('<ul class="errorlist"><li>Gif images are not allowed</li></ul>');
                    }      
                }
                else if(this.files[0].type.indexOf("image") == -1) {
                    $('#submit_cover_profile_btn').hide();
                    if ($('.errorlist').length) {
                        $('.errorlist').html('<li>Please upload a valid image</li>');
                    }
                    else {
                        $('.upload_pforile_cover_form').prepend('<ul class="errorlist"><li>Please upload a valid image</li></ul>');
                    }      
                }       
                else{
                    $('#submit_cover_profile_btn').show();
                    $('.errorlist').html(''); 
                }        
        });


        $("#send_message").click(function(event){
            event.preventDefault();
            event.stopPropagation();
            var self = $(this);
            if (self.data('toggled')) {
                $('.send_message_form').hide();
                self.data('toggled',false);
            }
            else {
                $('.send_message_form').show();
                self.data('toggled',true);
            }
        });

        $(document).on('submit', ".send_message_form", function(e) {
            e.preventDefault();
            var self = $(this);
            var url = self.attr('action');
            make_request({
                url:url,
                data: self.serialize(),
                callback: function(data) {
                    if (data.status == 'OK') {
                        console.log(' all good' );
                        $('#id_content').val('');
                        self.hide();
                        $("#send_message").data('toggled',false);
                    }
                }
            });
        });

        $('.noPhoto').hover(
            function(){
                $('.upload').show();
            },
            function(){
                $('.upload').hide();
            }
        );

        $('.profile_cover').hover(
            function(){
                $('.upload_cover').show();
            },
            function(){
                $('.upload_cover').hide();
            }
        );

        /** reposition page cover image */
        $(document).on('click','#save_image_profile',function(e){
            e.preventDefault();
            var post = $('.profile_cover').position();
            var url = 'reposition/';
            var pattern = /url\(|\)|"|'/g;
            make_request({
                url:url,
                data:{
                    'top':post.top,
                    'image':$('.profile_cover').css('backgroundImage').replace(pattern,""),
                },
                callback:function(data) {
                    history.go(0);
                }
            });
        });
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
            if($(this).val() === '') {
                $(this).val("Share something...");
            }
        });


        $("#postboxbutton").click(function() {
            var options = {
                url: "/posts/save/",
                type: "POST",
                dataType: "JSON",
                beforeSubmit: function() {
                    var loading = $('<div class="large_loader" style="padding-left: 0;"></div>');
                    $('#attached-images ul').html(loading);
                },
                success: function(data) {
                    if (data.status === 'OK') {
                        $("#news_feed").prepend(data.html);
                        $('.postbox_textarea').val('');
                        console.log('saving');
                        make_excerpts();
                    } else {
                        if ($('.errorlist').length) {
                            $('.errorlist').html(data.errors);
                        }
                        else {
                            $('#attached-images').append('<ul class="errorlist">' + data.errors + '</ul>');
                        }
                    }
                    $("#attached-images ul").html("");
                    LionFace.PostImages.bind_settings($('#news_feed .post_feed:first'));
                    this.attach_image_count = 0;
                },
                error: function() {
                    $('#attached-images ul').html('Error.');
                }
            };
            $("#postform").ajaxSubmit(options);
            return false;
        });

        $(document).on('click','.post_option',function(){
            $(this).find('input').prop('checked', true);
        });

        $('#postbox').on('dragover', function(e) {
            e = e.originalEvent;
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
        }).on('drop', this.attach_dropped_image);

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

        $('#attached-images').sortable();
        $('.postbox_textarea').autosize();
    },

    attach_image: function(event) {
        event.preventDefault();
        if (this.attach_image_count > MAX_UPLOAD_IMAGES) {
            create_message("Too many images", "error");
            return;
        }
        var $attached_images = $('#attached-images');
        $attached_images.find("ul").append("<li><input class='attach-image-file' type='file' name='image' style='display: none;'></li>");
        // document.getElementsByClassName('attach-image-file')[0].addEventListener('change', uploadImage, false);
        $(".attach-image-file").on("change", function(e) {
        // function uploadImage(e) {
            // TODO: check uploaded image size
            // if(e.target.files[0].size > 3145728) {
            var image = e.target.files[0];
            if (image === undefined) {
                console.log('file not select');
                return;
            }
            window.loadImage(
                image,
                function (img) {
                    $attached_images.find("ul li:last").append(img);
                    // $attached_images.sortable();
                },
                {
                    maxWidth: 190
                }
            );
        });
        $attached_images.find(".attach-image-file:last").click();
        this.attach_image_count += 1;
    },

    attach_dropped_image: function (e) {
        console.log('1');
        var $attached_images = $('#attached-images');
        e = e.originalEvent;
        e.preventDefault();
        var image = (e.dataTransfer || e.target).files[0];
        console.log(image);
        window.loadImage(
            image,
            function (img) {
                $attached_images.find('ul').append(img);
                var data = {
                    image: image
                };
                // $.post('/posts/save/', data, function (data) {
                //     alert('hi');
                // }, 'JSON');
                console.log(img);
            },
            {
                maxWidth: 190
            }
        );
    },

    bind_albums : function() {
    /*********** Albums ***********/
        var self_class = this;

        /** Create album */
        $(document).on('submit','#create_album_form',function(e) {
            e.preventDefault();
            var self = $(this);
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
                        self.hide();
                        if ($('#create_album_link').data('toggled')) {
                            $('#create_album_link').data('toggled',false);
                        }
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
