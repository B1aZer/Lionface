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
})
