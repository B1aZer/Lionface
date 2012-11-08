LionFace.PagesSettings = function() {
    this.runner();
}


LionFace.PagesSettings.prototype = {

    runner : function() {
        this.bind_functions();

    },

    //Binding
    bind_functions : function() {
    $('#privacy').hide();

    $(document).on('click','#admins_settings',function(){
        $('#basics').hide();
        $('#basics_header').hide(); 
        $('#basics_settings').removeClass('active');
        $('#privacy').show();
        $('#privacy_header').show(); 
        $('#admins_settings').addClass('active');
        $('#submit_button').hide();
    });

    $(document).on('click','#basics_settings',function(){
        $('#basics').show();
        $('#basics_header').show(); 
        $('#basics_settings').addClass('active');
        $('#privacy').hide();
        $('#privacy_header').hide(); 
        $('#admins_settings').removeClass('active');
        $('#submit_button').show();
    });

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

    },
}

$(function() {         
    LionFace.PagesSettings = new LionFace.PagesSettings();
});

