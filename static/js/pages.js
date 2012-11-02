LionFace.Pages = function() {
    this.runner();
}


LionFace.Pages.prototype = {

    runner : function() {
        self_class = this;
        this.bind_functions();
        this.bind_page_functions();
        if (LionFace.User.page_id) {
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
        $(document).on('click','.love_button',function(e) {
            e.preventDefault();
            var me = $(this);
            var url = '/pages/love_count/';
            var vote = 'up';
            var love_count = parseInt($('.love_count').html());
            if ($(this).hasClass('loved')) {
                vote = 'down';
            }
                make_request({
                    url:url,
                    data: {
                        'vote': vote,
                        'page_id': LionFace.User.page_id,
                    },
                    callback: function(data) {
                        if (data.status == 'OK') {
                            if (vote == 'up') {
                                me.html('Loved');
                                me.addClass('loved');   
                                love_count = love_count + 1;
                                
                            }
                            else {
                                me.html('Love');
                                me.removeClass('loved'); 
                                love_count = love_count - 1;
                            }
                            $('.love_count').html(love_count);
                        }
                    }
                });
        });
    },

    bind_page_functions : function() {

        /** micro templates */
        $(document).on('click','.page_btn',function(e) {
            e.preventDefault();
            var name = $(this).attr('id');
            var url = "?ajax"
            make_request({
                url:url,
                type:'GET',
                data: {
                    'template_name': name,
                },
                callback: function(data) {
                    if (data.html) {
                        $('.page_container').html(data.html);
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
        }) 
    },
    load_page_feed : function(elem, page) {
        var elem = elem || $('#page_feed');
        var page = page || 1;
        console.log(page);
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
