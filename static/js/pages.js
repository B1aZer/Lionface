LionFace.Pages = function() {
    this.runner();
}


LionFace.Pages.prototype = {

    runner : function() {
        self_class = this;
        this.bind_functions();
        this.bind_page_functions();
        if (LionFace.User.page_list) {
            this.load_page_feed(); 
        }
    },

    //Binding
    bind_functions : function() {
        $(document).on('click','#business_submit',function(e) {
            e.preventDefault();
            var select = $('<select name="type" id="id_type" >' +
                    '<option value="BS" selected="selected">Business Page</option>' +
                    '<option value="NP">Nonprofit Page</option>' +
                    '</select>')
            select.hide();
            $(this).append(select);
            $('#business_submit_form').submit();
        });

        $(document).on('click','#nonprofit_submit',function(e) {
            e.preventDefault();
            var select = $('<select name="type" id="id_type" >' +
                    '<option value="BS">Business Page</option>' +
                    '<option value="NP" selected="selected">Nonprofit Page</option>' +
                    '</select>')
            select.hide();
            $(this).append(select);
            $('#nonprofit_submit_form').submit();
        });

        /** label for */
        $(document).on('click','label',function(e) {
            var checkbox = $(this).prev('input')
            if (checkbox.prop("checked")) {
                checkbox.prop('checked', false);
            }
            else {
                checkbox.prop('checked', true);
            }
        });

        /** love counts */
        // moved to site.js

    },

    bind_page_functions : function() {

        /** micro templates */
        $(document).on('click','.page_btn',function(e) {
            e.preventDefault();
            var name = $(this).attr('id');
            var url = "?ajax"
            var self = $(this);
            make_request({
                url:url,
                type:'GET',
                data: {
                    'template_name': name,
                },
                callback: function(data) {
                    if (data.html) {
                        $('.page_container').html(data.html);
                        if ($('.business_on').length) {
                            $('.business_on').removeClass('business_on');
                            self.addClass('business_on');
                        }
                        if ($('.nonprofit_on').length) {
                            $('.nonprofit_on').removeClass('nonprofit_on');
                            self.addClass('nonprofit_on');
                        } 
                        if (name == 'updates') {
                             self_class.load_page_feed();
                        }
                    }
                }
            });
        });

        /** update button */
        $(document).on('click','#postboxbutton',function(e) {
            e.preventDefault();     
            var url = "/pages/update/";
            var content = $('.postbox_textarea').val();
            if (content) {
                make_request({
                    url:url,
                    data: {
                        'page_id': LionFace.User.page_id,
                        'content': content,
                    },
                    callback:function(data) {
                        if (data.status == 'OK') {
                            $('.postbox_textarea').val('');
                            self_class.load_page_feed();
                        }
                    }
                });
            }
        });

        /** Load more post in pagefeed */
        $(document).on('click','#see_more_feed',function(e){
            e.preventDefault();
            var self = $(this)
            var page = get_int(self.attr('href'));
            if ($("#page_feed").length) {
                $("#page_feed").append("<div id='new_posts'></div>");
                $("#new_posts").addClass($("#page_feed").attr('class'));
            }
            self.remove();
            self_class.load_page_feed($("#new_posts"), page);
        });

        /** reposition page cover image */
        $(document).on('click','#save_image',function(e){
            e.preventDefault();
            var post = $('#cover_image').position();
            var url = 'reposition/';
            var pattern = /url\(|\)|"|'/g;
            make_request({
                url:url,
                data:{
                    'top':post.top,
                    'image':$('#cover_image').css('backgroundImage').replace(pattern,""),
                },
                callback:function(data) {
                    location.reload();
                }
            });
        });

        /** upload form */
        $('.cover_photo').hover(
                function(){$('.upload_page').show();},
                function(){$('.upload_page').hide();}
        );

        $(document).on('click','#upload_cover_picture',function(e){ 
            $('.upload_cover_form').show();
        });

        /** restrict image uploads */
         $(document).on('change','#id_cover_photo',function() {
                if(this.files[0].size > 3145728) {  
                    $('#submit_cover_btn').hide();
                    if ($('.errorlist').length) {
                        $('.errorlist').html('<li>Image file too large ( &gt; 3mb )</li>');
                    }
                    else {
                        $('.upload_cover_form').prepend('<ul class="errorlist"><li>Image file too large ( &gt; 3mb )</li></ul>');
                    } 
                }
                else if(this.files[0].type == 'image/gif') {
                    $('#submit_cover_btn').hide();
                    if ($('.errorlist').length) {
                        $('.errorlist').html('<li>Gif images are not allowed</li>');
                    }
                    else {
                        $('.upload_cover_form').prepend('<ul class="errorlist"><li>Gif images are not allowed</li></ul>');
                    }      
                }
                else if(this.files[0].type.indexOf("image") == -1) {
                    $('#submit_cover_btn').hide();
                    if ($('.errorlist').length) {
                        $('.errorlist').html('<li>Please upload a valid image</li>');
                    }
                    else {
                        $('.upload_cover_form').prepend('<ul class="errorlist"><li>Please upload a valid image</li></ul>');
                    }      
                }       
                else{
                    $('#submit_cover_btn').show();
                    $('.errorlist').html(''); 
                }        
        });

        var edit_a = $('#edit_page_text').clone();
        var edit_url = edit_a.attr('href');

        //inline edit of the page's context
        $(document).on('click','#edit_page_text',function(e){
            e.preventDefault();
            var content = $('#page_inner_context').html();
                                        
            var edit_btn = $(this);
            var edit_input = $('<textarea>', {id: 'edit_input',
                                            rows: '4',
                                            cols: '65',
                                            maxlength: '225'});
            $('#page_content').html(edit_input);
            //trim
            content = String(content).replace(/^\s+|\s+$/g, '');
            if (content) {
                content = content.replace(/<br>/g,'\n');
                edit_input.val(content);
            }
            edit_input.focus(); 
        });

        $(document).on('blur','#edit_input',function() {
            var edit_input = $(this);
            var content = edit_input.val(); 
            make_request({
                url:edit_url,
                data:{
                    'content':content,
                },
                callback: function(data) {
                    if (data.status == 'OK') {
                        edit_input.replaceWith(data.html);
                    }
                }
            });
        });

        /** page friend request */
        $(document).on('click','.page_add_friend, .page_remove_friend', function(e) {
            e.preventDefault();
            var self = $(this);
            var url = self.attr('href');
            var send_data = $('#page_choose_select').val();
            if (!self.hasClass('request_sent')) {
                make_request({
                    url:url,
                    data:{
                        'page_id':send_data,
                    },
                    callback:function(data) {
                        if (data.status == 'OK') {
                            if (data.pages) {
                                // if choosing from select
                                $('#page_chooose_div').append(data.pages);
                                $('#page_choose_select').focus();
                                // hide other button
                                if (self.hasClass('page_remove_friend')) {
                                    $('.page_add_friend').hide();
                                }
                                else {
                                    $('.page_remove_friend').hide();
                                }
                            }
                            else {
                                if (self.hasClass('page_remove_friend')) {
                                    if (!data.pages_count) {
                                        self.remove();
                                    }
                                    $('.page_add_friend').show();
                                }
                                else {
                                    self.html('Page request sent');
                                    self.addClass('request_sent');
                                    $('.page_remove_friend').show();
                                }
                                $('#page_choose_select').remove();
                            }
                        }
                        else {
                            $('#page_choose_select').remove();
                        }
                    }
                });
            }
        });

    },
    load_page_feed : function(elem, page) {
        var elem = elem || $('#page_feed');
        var page = page || 1;
        var url = 'list_posts/'
        var loading = $('<div class="large_loader"></div>');
        elem.html(loading);
        make_request({
            url:url,
            type:'GET',
            data:{
                'page':page,
            },
            callback : function(data) {
                if (data.status == 'OK') {
                    if (page > 1) {
                        elem.replaceWith(data.html);
                    }
                    else {
                        elem.html(data.html);
                    }
                    make_excerpts();
                }
                else {
                    elem.html('');
                }
            },
            errorback : function() {
                elem.html('');
            }
        })
    }
}

$(function() {         
    LionFace.Pages = new LionFace.Pages();
});
