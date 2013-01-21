/*
function ReverseContentDisplay(d) {
    if(d.length < 1) { return; }
    if(document.getElementById(d).style.display == "none") { document.getElementById(d).style.display = "block"; }
    else { document.getElementById(d).style.display = "none"; }
}
*/

$(document).ready(function() {

    $(document).on('click','.public_link',function() {
        var name = $(this).attr('id');
        var url = '/micro/';
        var self = $(this);
        $.ajax(url,{
                type: 'GET',
                data: 'name=' + name,
                success: function(data) {
                    if(data.status == 'OK') {
                        $('.enabled_results').html(data.html);
                        $('.enabled_results').show();
                        $('.container_active').removeClass('container_active');
                        self.addClass('container_active');
                    }
                },
                error: function() {
                    console.log('error at public retrieval');
                }
            });
    });

    var random = Math.round(Math.random() * 10);
    $('.public_link').eq(random).click();

    $(document).on('click', '.about_tags', function() {
        var url = '/tag/?models=tags_tag&q=';
        var tag = $(this).find('.tag_name').html();
        url = url + tag;
        window.location = url;
    });

    $(document).on('click', '.about_users', function() {
        var url = $(this).find('.user-link').attr('href');
        window.location = url;
    });

    $(document).on('click', '.about_pages', function() {
        var url = $(this).find('.page-link').attr('href');
        window.location = url;
    });

    ////// Pending activation page //////

    $(document).on('click', '#change_email', function(e) {
        e.preventDefault();
        $('#email_error').hide();
        $('#email_text').hide();
        $('#input_email').show();
        $('#input_email').focus();
        $('#resend_email').hide();
        $('.edit_email').show();
        $(this).hide();
    });

    /*
    $(document).on('click', '#cancel_email', function(e) {
        e.preventDefault();
        $('#input_email').val('').hide();
        $('#email_text').show();
        $('#resend_email').show();
        $('.edit_email').hide();
        $('#change_email').show();
    });
    */

    /*
    $(document).on('click', '#save_email', function(e) {
        e.preventDefault();
        var url = $(this).attr('href');
        $.ajax({
            url:url,
            type:'POST',
            data:{'email':$('#input_email').val()},
            success: function(data) {
                if (data.status == 'OK') {
                    $('#email_text').html($('#input_email').val());
                    $('#input_email').val('').hide();
                    $('#email_text').show();
                    $('#resend_email').show();
                    $('.edit_email').hide();
                    $('#change_email').show();
                }
                else {
                    if (data.error_email) { $('#email_error').show(); }
                    $('#input_email').val('').hide();
                    $('#email_text').show();
                    $('#resend_email').show();
                    $('.edit_email').hide();
                    $('#change_email').show();
                }
            }
        });
    });
    */
});
