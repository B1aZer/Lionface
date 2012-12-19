LionFace.Pages = function() {
    this.runner();
}


LionFace.Pages.prototype = {

    runner : function() {
        self_class = this;
        this.bind_functions();
        this.bind_page_functions();
        if (LionFace.User.options['pages_community__'+LionFace.User.page_id]) {
            LionFace.User.Pages_sortable_friends();
            this.community_micro();
        }
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

        /** collapsable reqeusts micro community */
        $(document).on('click','#emloyees_req_collapse',function(e) {
            e.preventDefault();
            var self = $(this)
            if (!self.data('toggled')) {
                self.data('toggled',true);
                $('#emplyees_past_table').slideDown();
            }
            else {
                self.data('toggled',false);
                $('#emplyees_past_table').slideUp();
            }
        });
        
        $(document).on('click','#interns_req_collapse',function(e) {
            e.preventDefault();
            var self = $(this)
            if (!self.data('toggled')) {
                self.data('toggled',true);
                $('#interns_past_table').slideDown();
            }
            else {
                self.data('toggled',false);
                $('#interns_past_table').slideUp();
            }
        });

        $(document).on('click','#volunteers_req_collapse',function(e) {
            e.preventDefault();
            var self = $(this)
            if (!self.data('toggled')) {
                self.data('toggled',true);
                $('#volunteers_past_table').slideDown();
            }
            else {
                self.data('toggled',false);
                $('#volunteers_past_table').slideUp();
            }
        });

        //hide hidden rows in pages nonprofits
        $('.hidden_row').hide();

        $(document).on('click','.browse_rows',function(e) {
            e.preventDefault();
            var tr = $(this).parents('tr')
            var category = tr.attr('class');
            if (!tr.data('toggled')) {
                $("." + category + ".hidden_row").show();
                $("." + category + ".page_row").show();
                tr.data('toggled',true);
                tr.data('entangled',false);
            }
            else {
                $("." + category + ".hidden_row").hide();
                tr.data('toggled',false);
            }
        });

        /** update button */
        $(document).on('click','.categoty_button',function(e) {
            e.preventDefault();
            var tr = $(this).parents('tr')
            var category = tr.attr('class');
            if (!tr.data('entangled')) {
                $("." + category + ".page_row").hide();
                $("." + category + ".hidden_row").hide();
                tr.data('entangled',true);
                tr.data('toggled',false);
            }
            else {
                $("." + category + ".page_row").show();
                tr.data('entangled',false);
            }
        });

    },

    bind_page_functions : function() {

        /** micro templates */
        $(document).on('click','.page_btn',function(e) {
            e.preventDefault();
            var name = $(this).attr('id');
            var url = "?ajax"
            var self = $(this);
            var right = !$(this).hasClass('grayed_out');
            if (right) {
                make_request({
                    url:url,
                    type:'GET',
                    data: {
                        'template_name': name,
                    },
                    callback: function(data) {
                        if (data.html) {
                            //remove calendar dialog dupl's
                            $('.not-dialog').remove();
                            $('.time-picker').remove();

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
            }
        });

        /** update button */
        $(document).on('click','#postboxbutton',function(e) {
            create_message();
            $('.postbox_errors').hide();
            e.preventDefault();     
            var url = "/pages/update/";
            var rating = false;
            if ($(this).hasClass('feedback_post')) {
                url = "/pages/feedback/";
                rating = get_int($('.final_review').attr('id'));
            }
            var content = $('.postbox_textarea').val();
            if (rating || !$(this).hasClass('feedback_post')) {
                if (content) {
                    make_request({
                        url:url,
                        data: {
                            'page_id': LionFace.User.page_id,
                            'content': content,
                            'rating': rating,
                        },
                        callback:function(data) {
                            if (data.status == 'OK') {
                                $('.postbox_textarea').val('');
                                if (rating) {
                                    self_class.load_feedback_feed();
                                }
                                else {
                                    self_class.load_page_feed();
                                }
                            }
                        }
                    });
                }
            }
            else {
                //create_message('Please, provide a valid rating.','error');
                $('.postbox_errors').show();
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

        /** upload cover form */
        $('.cover_photo').hover(
                function(){$('.upload_page').show();},
                function(){$('.upload_page').hide();}
        );

        $(document).on('click','#upload_cover_picture',function(e){ 
            $('.upload_cover_form').show();
        });
        $(document).on('click', '#cancel_cover_btn', function(event) {
            $('.upload_cover_form').fadeOut(function(){
                $('#id_cover_photo').val('');
            });
            return false;
        });

        /** upload image form */
        $('.page_image').hover(
            function() {
                $(this).find('div').fadeIn();
            },
            function() {
                $(this).find('div').fadeOut();
            }
        ).click(function(event) {
            if (!$(document.elementFromPoint(event.clientX, event.clientY)).is('a')) {
                window.location.href = $(this).data('url');
            }
        }).find('#upload_album_image').click(function(event) {
            $('.upload_album_form').show();
            return false;
        });
        $(document).on('click', '#cancel_album_image_btn', function(event) {
            $('.upload_album_form').fadeOut(function(){
                $('#id_image').val('')
            });
            return false;
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
            if (!(self.hasClass('request_sent')) && !(self.hasClass('friend_removed'))) {
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
                                    self.html('Removed');
                                    self.addClass('friend_removed');
                                    if (!data.pages_count) {
                                        self.remove();
                                    }
                                    $('.page_add_friend').show();
                                }
                                else {
                                    self.html('Sent');
                                    self.addClass('request_sent');
                                    $('.page_remove_friend').show();
                                }
                                $('#page_choose_select').remove();
                                $('.choose_help').remove();
                            }
                        }
                        else {
                            $('#page_choose_select').remove();
                            $('.choose_help').remove();
                        }
                    }
                });
            }
        });

        // hide friends icons, if we have more than 4
        // moved to template micro/_friends.html
        // show them
        $(document).on('click','.show_more_friends',function(e) {
            e.preventDefault();
            var self = $(this);
            if (!self.data('shown')) {
                if (self.hasClass('business_friends_show')) {
                    $('.friend_busn_hidden').show();
                }else{
                    $('.friend_nonp_hidden').show();
                }
                self.data('shown',true);
                self.html('Hide');
            }
            else {
                if (self.hasClass('business_friends_show')) {
                    $('.friend_busn_hidden').hide();
                }else{
                    $('.friend_nonp_hidden').hide();
                }
                self.data('shown',false);
                self.html('Show');
            }
        });   

        //on mouse over icon name
        $(document).on("mouseenter", ".friend_icon", function(){
            $(this).find('.friend_name').show();
        }).on("mouseleave", ".friend_icon", function(){
            $(this).find('.friend_name').hide();
        });


        // hide loves icons, if we have more than 1 row
        //moved to community.html
        // show them
        $(document).on('click','.community_see_more',function(e) {
            e.preventDefault();
            var self = $(this);
            var content = self.find('div');
            var lovers = self.hasClass('lovers_link');
            var interns = self.hasClass('interns_link');
            var emloyees = self.hasClass('emloyees_link');
            var volunteers = self.hasClass('volunteers_link');
            if (!self.data('shown')) {
                if (lovers) {
                    $('.loves_hidden').show();
                }
                if (interns) {
                    $('.interns_hidden').show();
                }
                if (emloyees) {
                    $('.emloyees_hidden').show();
                }
                if (volunteers) {
                    $('.volunteers_hidden').show();
                }
                self.data('shown',true);
                content.html('See Less');
            }
            else {
                if (lovers) {
                    $('.loves_hidden').hide();
                }
                if (interns) {
                    $('.interns_hidden').hide();
                }
                if (emloyees) {
                    $('.emloyees_hidden').hide();
                }
                if (volunteers) {
                    $('.volunteers_hidden').hide();
                }
                self.data('shown',false);
                content.html('See More');
            }
        }); 

        $(document).on('click','.feedback_opinion',function(e) {
            e.preventDefault();
            var url = $(this).attr('href');
            var self = $(this);
            if (self.hasClass('agrees')) {
                var count = self.siblings('.feedback_agreed_count');
                var new_label = 'Agreed';
                var old_label = 'Agree';
                var sibling = self.siblings('.disagrees');
                var sibling_count = self.siblings('.feedback_disagreed_count');
            }
            else {
                var count = self.siblings('.feedback_disagreed_count');
                var new_label = 'Disagreed';
                var old_label = 'Disagree';
                var sibling = self.siblings('.agrees');
                var sibling_count = self.siblings('.feedback_agreed_count');
            }
            var value = parseInt(count.html());
            make_request({
                url:url,
                callback: function(data) {
                    if (data.status == 'OK') {
                        self.html(new_label);
                        sibling.hide();
                        sibling_count.hide();
                        value = value + 1;
                        count.html(value);
                        if (value == 1) {
                            count.show();
                        }
                    }
                    if (data.status == 'change') {
                        sibling.show();
                        if (parseInt(sibling_count.html())) {
                            sibling_count.show();
                        }
                        self.html(old_label);
                        value = value - 1;
                        count.html(value);
                        if (!value) {
                            count.hide();
                        }
                    }
                }
            });
        });

        $('.postbox_textarea').autosize();

        $(document).on('click','.page_delt_not',function(e) {
            e.preventDefault();
            var container = $(this).parents('.for_delt_notf');
            var url = $(this).attr('href');
            make_request({
                url:url,
                callback: function(data) {
                    if (data.status == 'OK') {
                        container.remove();
                    }
                }
            });
        });

        $(document).on('click','#duscussbutton',function(e) {
            e.preventDefault();
            var url = $(this).attr('href');
            if ($("#topicForm").valid()) {
                make_request({
                    url:url,
                    data:$("#topicForm").serialize(),
                    callback: function(data) {
                        if (data.status == 'OK') {
                            $('.page_center').replaceWith(data.html);
                        }
                    }
                });
            }
        });

        $(document).on('click','.page_topics',function(e) {
            e.preventDefault();
            var topic_id = get_int($(this).attr('id'));
            var url = 'list_topic/'+ topic_id + '/';
            make_request({
                url:url,
                callback: function(data) {
                    if (data.status == 'OK') {
                        $('.page_center').replaceWith(data.html);
                    }
                }
            });
        });
        
        /** topic post button */
        $(document).on('click','#posttopicbutton',function(e) {
            e.preventDefault();     
            var url = $(this).attr('href');
            var content = $('.postbox_textarea').val();
            if (content) {
                make_request({
                    url:url,
                    data: {
                        'content': content,
                    },
                    callback:function(data) {
                        if (data.status == 'OK') {
                            $('.page_center').replaceWith(data.html);
                        }
                    }
                });
            }
        });

        $(document).on('change','#id_privacy', function(e) {
            privacy = $(this).val();
            if (privacy == 'P') {
                $('#topic_tagged').hide();
                $('#topic_members').hide();
            }
            if (privacy == 'I') {
                $('#topic_tagged').show();
                $('#topic_members').show();
            }
            if (privacy == 'H') {
                $('#topic_tagged').hide();
                $('#topic_members').show();
            }
        });
        
    },
    /*
     * moved to user.js
    sortable_friends : function () {
    },
    */
    community_micro : function() {
        
        $(document).on('change','.community_checkbox',function() {
            var self = $(this);
            var name = self.attr('id');
            var url = 'community_check' + '/';
            var checked = self.prop('checked');
            if (name == 'employees_checkbox') {
                var content_div = '#employees_div';
                var menu_a = '#employee_flag';
            }
            if (name == 'interns_checkbox') {
                var content_div = '#interns_div';
                var menu_a = '#intern_flag';
            }
            if (name == 'volunteers_checkbox') {
                var content_div = '#volunteers_div';
                var menu_a = '#volunteer_flag';
            }
            make_request({
                url:url,
                data: {
                    'name':name,
                    'checked':checked,
                },
                callback: function(data) {
                    if(data.status =='OK') {
                        if(!checked){
                            $(content_div).hide();
                            $(menu_a).hide();
                            if (!$('#employees_checkbox').prop('checked') &&
                                !$('#interns_checkbox').prop('checked') &&
                                !$('#volunteers_checkbox').prop('checked')) {
                                $('#community_add_button').hide();
                            }

                        }
                        else {
                            $(content_div).show();
                            $(menu_a).show();
                            //add button
                            $('#community_add_button').show();
                        }
                    }
                    
                }
            });
        });
        
        //inline edit of the community's context  
        $(document).on('click','.add_community_info',function(e){
            e.preventDefault();
            var edit_div = $(this);
            var content = $(this).html();
                                        
            var edit_input = $('<textarea>', {id: 'edit_info',
                                            rows: '4',
                                            cols: '65',
                                            maxlength: '500'});
            edit_div.replaceWith(edit_input);
            content = String(content).replace(/^\s+|\s+$/g, '');
            if (content) {
                content = content.replace(/<br>/g,'\n');
                edit_input.val(content);
            }
            edit_input.focus(); 
        });

        $(document).on('blur','#edit_info',function() {
            var edit_input = $(this);
            var content = edit_input.val(); 
            var edit_url = 'community_text'+'/';
            var parent_id = edit_input.parent().attr('id');
            make_request({
                url:edit_url,
                data:{
                    'content':content,
                    'parent_id':parent_id,
                },
                callback: function(data) {
                    if (data.status == 'OK') {
                        edit_input.replaceWith(data.html);
                    }
                }
            });
        });         

        $(document).on('click','.confirm_community_req',function(e) {
            e.preventDefault();
            var url = $(this).attr('href');
            var tr = $(this).parents('tr');
            var parent_div = $(this).parents('.community_req_div');
            var parent_table = $(this).parents('table');
            make_request({
                url:url,
                callback: function(data) {
                    if (data.status == 'OK') {
                        tr.remove();
                        if (!parent_table.find('tr').length) {
                            if (parent_table.hasClass('past_table')) {
                                parent_div.find('.req_collapse').remove();
                            }
                            parent_table.remove();
                        } 
                        if (!parent_div.find('tr').length) {
                            parent_div.remove();   
                        }
                        $('#page_members_id').html(data.html);
                    }
                }
            });
        });

        $(document).on('click','.deny_community_req',function(e) {
            e.preventDefault();
            var url = $(this).attr('href');
            var tr = $(this).parents('tr');
            var parent_div = $(this).parents('.community_req_div');
            var parent_table = $(this).parents('table');
            make_request({
                url:url,
                callback: function(data) {
                    if (data.status == 'OK') {
                        tr.remove();
                        if (!parent_table.find('tr').length) {
                            if (parent_table.hasClass('past_table')) {
                                parent_div.find('.req_collapse').remove();
                            }
                            parent_table.remove();
                        } 
                        if (!parent_div.find('tr').length) {
                            parent_div.remove();   
                        }
                    }
                }
            });
        });

        var clone;
        var class_date;
        $(document).on('click','.comm_req_date',function(e) {
            e.preventDefault();
            var self = $(this);
            clone = self.clone();
            if (self.hasClass('from_date_class')) {
                class_date = 'from_date';
            }
            else {
                class_date = 'to_date' ;
            }
            var id = get_int(self.attr('id'));
            /*var input_month = $('<select>', { id:id, class:"date_inline_month"+" "+class_date});*/
            /*var input_year = $('<select>', { id:id, class:"date_inline_year"+" "+class_date});*/
            /**
            input.datepicker({
                changeMonth: true,
                changeYear: true,
                onSelect: function(dateText,inst) {
                    console.log(inst);
                    console.log(dateText);
                    make_request({ 
                        url:url,
                        data: {
                            'date':dateText,
                            'date_type':class_date,
                            'id':inst.id,
                        },
                        callback: function(data) {
                            if (data.status =='OK') {
                                clone.html(data.html);
                            }
                        }
                    });
                },
                onClose: function(dateText,inst) {
                    input.replaceWith(clone);
                },
            });           
            */
            self.replaceWith('<span id="'+ id +'">' +
            '<select class="date_from former_member month_select"></select> ' +
            '<select class="date_from former_member year_select"></select>' +
            '<a href="#" class="member_button_save">save</a> <a href="#" class="member_button_cancel">cancel</a>' +
            '</span>');
            LionFace.Site.datedropdown("month_select", "year_select");
            /*input_month.focus();*/
        });

        $(document).on('click','.member_button_save',function(e) {
            var monthtext=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sept','Oct','Nov','Dec'];
            e.preventDefault();
            var parent = $(this).parent();
            var url = 'community_date/';
            var id = get_int($(this).parent().attr('id'));
            var date_month = $(this).parent().find('.month_select').val();
            var date_year = $(this).parent().find('.year_select').val(); 
            date_month = monthtext.indexOf(date_month) + 1;
            var dateText = date_month + '/' + date_year;
            make_request({ 
                        url:url,
                        data: {
                            'date':dateText,
                            'date_type':class_date,
                            'id':id,
                        },
                        callback: function(data) {
                            if (data.status =='OK') {
                                clone.html(data.html);
                                parent.replaceWith(clone);
                            }
                        }
                    }); 
        });

        $(document).on('click','.member_button_cancel',function(e) {
            e.preventDefault();
            $(this).parent().replaceWith(clone);
        });
        
        /*live_search*/
        $(document).on('keyup','#live_search_input', function() {
            var search = $(this).val();
            var show = false;
            $('.community_request_class').each(function(i,e) {
                var name = $(e).find('.req_full_name');
                var re = new RegExp('('+search+')', "gi");
                var highl = $('<span>', { class:'highlight' });
                if (name.text().match(re)) {
                    var repl = name.text().replace(re,"<span class='matched_name'>$1</span>");
                    name.html(repl);
                    show = true;
                }
                else {
                    name.html(name.text());
                }
            })
            if (!search) {
                show = false;
            }
            if (show) {
                $('#live_search_goto').show();
            }
            else {
                $('#live_search_goto').hide();
            }
        });

        $(document).on('click','#live_search_goto',function(e) {
            e.preventDefault();
            var search = $('#live_search_input').val().toLowerCase()
            var foundin = $('.community_request_class .req_full_name').filter(function() {
                return $(this).text().toLowerCase().indexOf(search) >= 0;
            });
            if (foundin.length > 1) {
                foundin = foundin.first();   
            }
            if (foundin.is(":visible")) {}
            else {
                foundin.parents('.past_table').show();
            }
            if ( foundin.length ) {
                $(window).scrollTop(foundin.offset().top-50);
            }
        })

    },
    load_page_feed : function(elem, page, type) {
        var elem = elem || $('#page_feed');
        var page = page || 1;
        var type = type || 'updates';
        if (type == 'feedback') {
            var url = 'list_feedback/';
        }
        else {
            var url = 'list_posts/';
        }
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
    },
    load_feedback_feed : function(elem, page, type) {
        var elem = elem || '';
        var page = page || '';
        var type = type || 'feedback';
        this.load_page_feed(elem, page, type);
    },
    /*
    populatedropdown : function(dayfield, monthfield, yearfield){
        var monthtext=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sept','Oct','Nov','Dec'];
        var today=new Date()
        var dayfield=document.getElementById(dayfield)
        var monthfield=document.getElementById(monthfield)
        var yearfield=document.getElementById(yearfield)
        for (var i=0; i<31; i++) dayfield.options[i]=new Option(i, i+1)
        dayfield.options[today.getDate()]=new Option(today.getDate(), today.getDate(), true, true) 
        //select today's day
        for (var m=0; m<12; m++) monthfield.options[m]=new Option(monthtext[m], monthtext[m])
        monthfield.options[today.getMonth()]=new Option(monthtext[today.getMonth()], monthtext[today.getMonth()], true, true) 
        //select today's month
        var thisyear=today.getFullYear()
        for (var y=0; y<20; y++){
        yearfield.options[y]=new Option(thisyear, thisyear)
        thisyear+=1
        }
        yearfield.options[0]=new Option(today.getFullYear(), today.getFullYear(), true, true) //select today's year
    },
    */
}

$(function() {         
    LionFace.Pages = new LionFace.Pages();
});
