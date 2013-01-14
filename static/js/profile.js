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
            this.bind_profile_functions();
        }
    },

    //restrict image size and format before upload
    bind_upload_form : function() {
        $('#id_photo').bind('change', function() {
                //console.log(this.files[0].type);
                //console.log(this.files[0].size);
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
        var _this = this;

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
                        make_excerpts();
                        LionFace.Site.revert_textbox_height();
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
                    LionFace.Site.attach_image_count = 0;
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
        }).on('drop', LionFace.Site.attach_dropped_image);

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

    bind_profile_functions : function () {

        //// Favourite Pages ////

        function split( val ) {
            return val.split( /,\s*/ );
        }
        function extractLast( term ) {
            return split( term ).pop();
        }    
        /** Autocomplete for pages */
        var url_auto_fav = LionFace.User.favourite_pages_url;
        $( "#favourite_pages_input" ).autocomplete({
            source: url_auto_fav,
        });

        /* //multiple pages 
        var url_auto = LionFace.User.favourite_pages_url;
        $("#favourite_pages_input")
            // don't navigate away from the field on tab when selecting an item
            .bind( "keydown", function( event ) {
                if ( event.keyCode === $.ui.keyCode.TAB &&
                        $( this ).data( "autocomplete" ).menu.active ) {
                    event.preventDefault();
                }
            })
            .autocomplete({
                source: function( request, response ) {
                    $.getJSON( url_auto, {
                        term: extractLast( request.term )
                    }, response );
                },
                focus: function() {
                    // prevent value inserted on focus
                    return false;
                },
                select: function( event, ui ) {
                    var terms = split( this.value );
                    // remove the current input
                    terms.pop();
                    // add the selected item
                    terms.push( ui.item.value );
                    // add placeholder to get the comma-and-space at the end
                    terms.push( "" );
                    this.value = terms.join( ", " );
                    return false;
                }
                
            }); 
        */

        $(document).on('click','#favorite-pages', function (e) {
            e.preventDefault();
            var self = $(this);
            if (self.data('toggled')) {
                $('.fav-pages').hide();
                $('#left_fav').hide();
                self.data('toggled',false);
            }
            else {
                $('.fav-pages').show();
                $('#left_fav').show();
                self.data('toggled',true);
            }
        });

        $(document).on('click','#cancel_favourite', function (e) {
            e.preventDefault();
            var self = $(this);
            $('#favourite_pages_input').val('');
            $('.fav-pages').hide();
            $('#left_fav').hide();
            $('#favorite-pages').data('toggled',false);
        });

        

        $(document).on('click','#add_favourite', function (e) {
            e.preventDefault();
            var url = LionFace.User.favourite_pages_add_url;
            var pages_usernames = $('#favourite_pages_input').val();
            if (pages_usernames) {
                var data = {'pages':pages_usernames};
            }
            else {
                var data = '';
            }
            if (data) {
                make_request({ 
                    url:url,
                    data:data,
                    callback: function (data) {
                        if (data.pages) {
                            $('#favorite-pages-container').html(data.pages);
                            $('#favorite-pages-container').show();
                            $('#favourite_pages_input').val('');
                            $('.fav-pages').hide();
                            $('#left_fav').hide();
                            $('#favorite-pages').data('toggled',false);
                        }
                    }
                });
            }
        });

        $(document).on('click','.rem-favourite-page', function(e) {
            e.preventDefault();
            var self = $(this);
            var url = self.attr('href');
            make_request({
                url:url,
                callback: function(data) {
                    if (data.status == 'OK') {
                        self.parents('.favorite_page').fadeOut();
                    }
                }
            });
        });

        // Making sortable
        var pos_bgn_pages = 0;

        $( ".sortable-pages" ).sortable({
            start: function(event, ui) {
                pos_bgn = ui.item.index();
            },
            stop: function(event, ui) {
                /*console.log("New position: " + ui.item.index());*/
                /*console.log("Old position: " + pos_bgn);*/
                var item_id = get_int(ui.item[0].id)
                url = 'favourites_reposition/'
                if (ui.item.index() != pos_bgn) {
                    make_request({
                        url:url,
                        data: {
                            page_id:item_id,
                            position_bgn:pos_bgn,
                            position_end:ui.item.index()
                        },
                        callback: function() {
                        }
                    });
                }
            }
        });
        $( ".sortable-pages" ).disableSelection();

        //// Relationships ////

        $(document).on('click','#inter_relation_btn', function(e) {
            e.preventDefault();
            var self = $(this);
            if (self.data('toggled')) {
                $('.inter-relation').hide();
                $('#left_rel').hide();
                $('.inter_relation_container').hide();
                self.data('toggled',false);
            }
            else {
                $('.inter-relation').show();
                $('#left_rel').show();
                if ($('#inter_relation_select').val() != 'S') {
                    $('.inter_relation_container').show();
                }
                self.data('toggled',true);
            }
        });

        $(document).on('change','#inter_relation_select', function(e) {
            var self = $(this);
            if (self.val() != 'S') {
                $('.inter_relation_container').show();
            }
            else {
                $('.inter_relation_container').hide();
                $('#inter_relation_input').val('');
            }
        });

        $(document).on('click','#cancel_inter_relation', function(e) {
            var self = $(this);
            e.preventDefault();
            $('.inter-relation').hide();
            $('#left_rel').hide();
            $('#inter_relation_btn').data('toggled',false);
            $('.inter_relation_container').hide();
            $('#inter_relation_input').val('');
        });



        $(document).on('click', '#save_inter_relation', function(e) {
            e.preventDefault();
            var url = LionFace.User.relation_add_url;
            var data = {'relationtype':$('#inter_relation_select').val()};
            if ($('#inter_relation_input').val()) {
                data['related'] = $('#inter_relation_input').val();
            }
            var single = data.relationtype == 'S';
            make_request({
                url:url,
                data:data,
                callback: function (data) {
                    if (data.status == 'OK') {
                        $('.inter-relation').hide();
                        $('#left_rel').hide();
                        $('#inter_relation_input').hide();
                        $('#inter_relation_input').val('');
                        $('#inter_relation_btn').data('toggled',false);
                        $('#relation_type_id').html(data.relation);
                        if (single) {
                            $('#inter_relation_input').show();
                        }
                        $('#realtions_container').replaceWith(data.html);
                    }
                }
            });
        });

        // BIO //

        $(document).on('click', '#save_bio_text', function(e) {
            e.preventDefault();
            var self = $(this);
            var url = self.attr('href');  
            var data = {'text': $('#bio_info_textarea').val()}
            make_request({
                url:url,
                data:data,
                callback: function (data) {
                    if (data.status == 'OK') {
                        $('.bio_info').hide();
                        $('#left_bio').hide();
                        $('#bio_info_text').html(data.text);
                        $('#bio_info_text').show();
                        $('#show_bio_info').data('toggled',false);
                    }
                }
            });
        });

        $(document).on('click', '#show_bio_info', function (e) {
            e.preventDefault();
            var self = $(this);
            if (self.data('toggled')) {
                $('.bio_info').hide();
                $('#left_bio').hide();
                $('#bio_info_textarea').val('');
                $('#bio_info_text').show();
                self.data('toggled',false);
            }
            else {
                if ($('#bio_info_text').html()) {
                    $('#bio_info_textarea').val($('#bio_info_text').html());
                }
                $('.bio_info').show();
                $('#left_bio').show();
                $('#bio_info_text').hide();
                self.data('toggled',true);
            }
        });

        $(document).on('click', '#cacel_bio_text', function (e) {
            e.preventDefault();
            $('.bio_info').hide();
            $('#left_bio').hide();
            $('#bio_info_textarea').val('');
            $('#bio_info_text').show();
            $('#show_bio_info').data('toggled',false);
        });
        

        $(document).on('click', '#show_birth_select', function (e) {
            e.preventDefault();
            var self = $(this);
            if (self.data('toggled')) {
                $('.birth_select').hide();
                $('#left_birth').hide();
                self.data('toggled',false);
            }
            else {
                var day = parseInt($('#birth_day_id').html());
                var month = parseInt($('#birth_month_id').attr('class')) - 1;
                var year = parseInt($('#birth_year_id').html());

                LionFace.Site.daydatedropdown('birth_day_select','birth_month_select','birth_year_select',day,month,year);
                $('.birth_select').show();
                $('#left_birth').show();
                self.data('toggled',true);
            }
        });

        $(document).on('click', '#save_birth_date', function (e) {
            e.preventDefault();
            var self = $(this);
            var day = $('.birth_day_select').val();
            var month = $('.birth_month_select').val();
            var year = $('.birth_year_select').val();
            var url = self.attr('href');
            if (day && month && year) {
                var data = {'datetext' : day + '/' + month + '/' + year} 
            }
            else {
                return;
            }
            make_request({
                url:url,
                data:data,
                callback: function (data) {
                    if (data.status == 'OK') {
                        $('.birth_select').hide();
                        $('#left_birth').hide();
                        $('#show_birth_select').data('toggled',false);
                        $('#birth_day_id').html(data.day);
                        $('#birth_month_id').html(data.month);
                        $('#birth_month_id').attr('class',data.month_d);
                        $('#birth_year_id').html(data.year);
                    }
                }
            });
        });
        
        $(document).on('click', '#cancel_birth_date', function (e) {
            e.preventDefault();
            $('.birth_select').hide();
            $('#left_birth').hide();
            $('#show_birth_select').data('toggled',false);
        });
        
        $(document).on('click', '#show_url_input', function (e) {
            e.preventDefault();
            var self = $(this);
            if (self.data('toggled')) {
                $('.bio_website').hide();
                $('.url_errors').hide();
                $('#left_web').hide();
                $('#url_input').val('');
                self.data('toggled',false);
            }
            else {
                $('.bio_website').show();
                $('#left_web').show();
                self.data('toggled',true);
            }
        });

        $(document).on('click', '#save_url_input', function (e) {
            e.preventDefault();
            var self = $(this);
            var url = self.attr('href');
            var data = {'url' : $('#url_input').val()};
            if (!data.url) {
                return;
            }
            make_request({
                url:url,
                data: data,
                callback : function (data) {
                    if (data.status == 'OK') {
                        $('.bio_website').hide();
                        $('#left_web').hide();
                        $('#show_url_input').data('toggled',false);
                        $('#url_container').html(data.link);
                        $('#url_input').val('');
                    }
                    if (data.error) {
                        $('.url_errors').show();
                    }
                    else {
                        $('.url_errors').hide();
                    }
                }
            });
        });

        $(document).on('click', '#cancel_url_input', function (e) {
            e.preventDefault();
            $('.bio_website').hide();
            $('#left_web').hide();
            $('#show_url_input').data('toggled',false);
            $('.url_errors').hide();
            $('#url_input').val('');
        });
        
        
    }

}

$(function() {
    LionFace.Profile = new LionFace.Profile();
    LionFace.Profile.hide_album_hint();

    // $li = $('#attached-images ul li');
    // $image_settings = $li.find('#image_settings');
    // console.log($li);
    // console.log($image_settings);
    // if ($image_settings.length != 1)
    //     return;
    // $image_settings.hide();
    // $li.hover(
    //     function() {
    //         $image_settings.show();
    //     },
    //     function() {
    //         $image_settings.hide();
    //     }
    // );

});
