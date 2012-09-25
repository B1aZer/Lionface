function show_basics() {
    ShowContent('basics');
    ShowContent('basics_header'); 
    HideContent('privacy'); 
    HideContent('privacy_header'); 
    $('#privacy_settings').removeClass('active');
    $('#basics_settings').addClass('active');
    $('#form_name').val('basics');
    return false;
}

function show_privacy() {
    ShowContent('privacy');
    ShowContent('privacy_header'); 
    HideContent('basics'); 
    HideContent('basics_header'); 
    $('#basics_settings').removeClass('active');
    $('#privacy_settings').addClass('active');
    $('#form_name').val('privacy');
    return false;
}

$(document).ready(function() {
    $('.active').click();
    $(document).on('click','#delete_account', function (e) {
        e.preventDefault();
        $('#delete_account_form').show().attr('style','display:inline');
        $('#submit_button').hide();
        $(this).hide();
        $('#id_confirm_pass').focus();
    });
    $('#id_confirm_pass').blur(function(e) { 
        if ($('#submit_delete').is(':hover') === false) {
            $('#delete_account').show()
            $('#submit_button').show();
            $('#delete_account_form').hide();
        }
    });
    $('#delete_account_form').submit( function() {
        data_send = $(this).serialize()
        url = $(this).attr('action');
        make_request({
            url:url,
            data:data_send,
            callback: function (data) {
                if (data.status == 'OK') {
                    window.location.href = data.redirect;
                }
                else {
                    $('.confirm_errors').html(data.message);
                    $('#id_confirm_pass').focus();
                }
            }
        });
        return false;
    });
    

})
