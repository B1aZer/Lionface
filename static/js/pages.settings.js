LionFace.PagesSettings = function() {
    this.runner();
}


LionFace.PagesSettings.prototype = {

    runner : function() {
        this.bind_functions();
        this.bind_loves();

    },

    //Binding
    bind_functions : function() {

        if ( $('#active_input').val() != 'loves' ) {
            $('#privacy').hide();
            $('#loves').hide();
        }
        
        if (LionFace.User.options['pages_admins__'+LionFace.User.page_id] &&
            !LionFace.User.options['pages_basics__'+LionFace.User.page_id]) {
                $('#basics').hide();
                $('#loves').hide();
                $('#privacy').show();
        }

        if (LionFace.User.options['pages_loves__'+LionFace.User.page_id] &&
            !LionFace.User.options['pages_basics__'+LionFace.User.page_id] &&
            !LionFace.User.options['pages_admins__'+LionFace.User.page_id]) {
                $('#basics').hide();
                $('#loves').show();
                $('#submit-card').show();
        }

        $(document).on('click','#admins_settings',function(){
            $('#basics').hide();
            $('#loves').hide();
            $('#basics_header').hide(); 
            $('#loves_header').hide(); 
            $('#basics_settings').removeClass('active');
            $('#loves_settings').removeClass('active');
            $('#privacy').show();
            $('#privacy_header').show(); 
            $('#admins_settings').addClass('active');
            $('#submit_button').hide();
            $('#submit-card').hide();
            $('#cancel-bid').hide();
            $('#active_input').val('admins');
        });

        $(document).on('click','#basics_settings',function(){
            $('#basics').show();
            $('#basics_header').show(); 
            $('#basics_settings').addClass('active');
            $('#privacy').hide();
            $('#loves').hide();
            $('#privacy_header').hide(); 
            $('#loves_header').hide(); 
            $('#admins_settings').removeClass('active');
            $('#loves_settings').removeClass('active');
            $('#submit_button').show();
            $('#submit-card').hide();
            $('#cancel-bid').hide();
            $('#active_input').val('basics');
        });

        $(document).on('click','#loves_settings',function(){
            $('#loves').show();
            $('#loves_header').show(); 
            $('#loves_settings').addClass('active');
            $('#privacy').hide();
            $('#basics').hide();
            $('#privacy_header').hide(); 
            $('#basics_header').hide(); 
            $('#admins_settings').removeClass('active');
            $('#basics_settings').removeClass('active');
            $('#submit-card').show();
            $('#submit_button').hide();
            $('#active_input').val('loves');
            $('#cancel-bid').show();
            if ( $('.no_bidding').length ) {
                $('#submit-card').hide();
            }
        });

        if ( $('#active_input').val() == 'loves' ) {
            $('#loves_settings').click();
        }

        $(document).on('click','#delete_page', function (e) {
            e.preventDefault();
            $('#delete_page_form').show().attr('style','display:inline');
            $('#submit_button').hide();
            $(this).hide();
            $('#id_confirm_pass').focus();
        });    

        $(document).on('blur','#id_confirm_pass',function(e) { 
            if ($('#submit_delete').is(':hover') === false) {
                $('#delete_page').show()
                $('#submit_button').show();
                $('#delete_page_form').hide();
            }
        });  

        /** Autocomplete for admins */
        var url_auto = '/auto_pages/';
        url_auto = url_auto + LionFace.User.page_slug + '/';
        $( "#id_admins" ).autocomplete({
            source: url_auto,
            select: function(event, ui) { 
                $('#add_admin').show();
            }
        }); 

        $(document).on('input','#id_admins',function() {
            if (!$(this).val()) {
                $('#add_admin').hide(); 
            }
        });

        $(document).on('click','#add_admin',function(e) { 
            e.preventDefault();
            var url = $(this).attr('href');
            var admin_username = $('#id_admins').val();
            make_request({
                url:url,
                data: {
                    'admin_username':admin_username,
                    'add': true,
                },
                callback: function(data) {
                    if (data.status == 'OK') {
                        $('.admins_list').html(data.html);
                        $('#id_admins').val('');
                        $('#add_admin').hide(); 
                    }
                }
            });
        });

        $(document).on('click','.remove_admins',function(e) { 
            e.preventDefault();
            var url = $(this).attr('href');
            var admin_username = $(this).attr('id');
            make_request({
                url:url,
                data: {
                    'admin_username':admin_username,
                    'remove': true,
                },
                callback: function(data) {
                    if (data.status == 'OK') {
                        $('.admins_list').html(data.html);
                    }
                }
            }); 
        });

        $(document).on('change','.page_options',function() {
            var url = '/pages/page/' + LionFace.User.page_slug + '/settings_admins/';
            var option = $(this).attr('id');
            make_request({
                url:url,
                data: {
                    'option': option,
                },
                callback: function(data) {
                    if (data.status == 'OK') {
                    }
                }
            });   
        });

        $(document).on('click','.admins_labels',function(e) {
            e.preventDefault;
            var checkb_id = '#' + $(this).attr('for');
            if ($(checkb_id).prop('checked')) {
                $(checkb_id).prop('checked', false);
            }
            else {
                $(checkb_id).prop('checked', true);
            }
        });

    },

    bind_loves: function() {
        $(document).on('click','#show_card_info',function(e) {
            e.preventDefault();
            if ($('#show_love_card_info').data('toggled')) {
                $('#card_info_loves').hide();
                $('#show_love_card_info').data('toggled',false);
            }
            if ($('#add_loves_card').data('toggled')) {
                $('#card_info_loves').hide();
                $('#add_loves_card').data('toggled',false);
            }
            if (!$(this).data('toggled')) {
                $('#card_info').show();
                $(this).data('toggled',true);
            }
            else {
                $('#card_info').hide();
                $(this).data('toggled',false);
            }
        });
        
        $(document).on('click','#show_love_card_info',function(e) {
            e.preventDefault();
            if ($('#show_card_info').data('toggled')) {
                $('#card_info').hide();
                $('#show_card_info').data('toggled',false);
            }
            if ($('#add_bidding_card').data('toggled')) {
                $('#card_info').hide();
                $('#add_bidding_card').data('toggled',false);
            }
            if (!$(this).data('toggled')) {
                $('#card_info_loves').show();
                $(this).data('toggled',true);
            }
            else {
                $('#card_info_loves').hide();
                $(this).data('toggled',false);
            }
        });
        
        $(document).on('click','#add_bidding_card',function(e) {
            e.preventDefault();
            if ($('#add_loves_card').data('toggled')) {
                $('#card_info_loves').hide();
                $('#add_loves_card').data('toggled',false);
            }
            if ($('#add_loves_card').data('toggled')) {
                $('#card_info_loves').hide();
                $('#add_loves_card').data('toggled',false);
            }
            if (!$(this).data('toggled')) {
                $('#card_info').show();
                $(this).data('toggled',true);
            }
            else {
                $('#card_info').hide();
                $(this).data('toggled',false);
            }
        });

        $(document).on('click','#add_loves_card',function(e) {
            e.preventDefault();
            if ($('#show_card_info').data('toggled')) {
                $('#card_info').hide();
                $('#show_card_info').data('toggled',false);
            }
            if ($('#add_bidding_card').data('toggled')) {
                $('#card_info').hide();
                $('#add_bidding_card').data('toggled',false);
            }
            if (!$(this).data('toggled')) {
                $('#card_info_loves').show();
                $(this).data('toggled',true);
            }
            else {
                $('#card_info_loves').hide();
                $(this).data('toggled',false);
            }
        });
               
    
    
    },
}

$(function() {         
    LionFace.PagesSettings = new LionFace.PagesSettings();
});

