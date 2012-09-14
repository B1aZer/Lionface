function auto_complete() {

 url = '/auto/';
    if (window.location.pathname.indexOf('/lionface/') >= 0) 
    { 
        url = '/lionface' +  url;
        url_user = '/lionface' +  url_user;
    }

$( "#id_user_to" ).autocomplete({
        source: url,
        select: function( event, ui ) {
            $( "#id_user_id" ).val( ui.item.id );
            $( "#id_user_to" ).val( ui.item.label );

            return false;
        }
    }).data( "autocomplete" )._renderItem = function( ul, item ) {
        return $( "<li></li>" )
        .data( "item.autocomplete", item )
        .append( "<a>" + item.label + '<div class="auto_subtext">' + item.value + '</div>' + "</a>" )
        .appendTo( ul );
    };    

}

function load_messages(user_id, sort) {

        if (!(user_id)) {
            return;
            }

         if (!(sort)) {
            sort = 'asc';
            } 

        url = "/messages/show/";

        if (window.location.pathname.indexOf('/lionface/') >= 0) 
        { 
            url = '/lionface' +  url;
        }  
        /*
        if (!($('.message_feed').length)) {
            var elem = $('<div class="message_feed"></div>');
            $('.right_col').prepend(elem);
        }
        */
        
        //loading
        var old_data = $('.right_col').html();
        $('.right_col').html('');
        $('.right_col').addClass("large_loader");

        $.ajax({
                type: 'POST',
                url: url,
                data: {
                    user_id : user_id,
                    sort : sort,
                },
                success: function(data) {
                    //remove loading
                    $('.right_col').removeClass("large_loader");
                    //old html
                    $('.right_col').html(old_data);
                    //remove To input
                    $('#id_user_to').parent().parent().hide();
                    //input user id
                    $( "#id_user_id" ).val( user_id );
                    //populate feed
                    if (sort == 'desc') {
                        if ($('.message_feed').length) {
                            $('.message_feed').remove();
                        }
                        var new_elem = $('<div class="message_feed"></div>').html(data.html);
                        $('.right_col').append(new_elem);
                    }
                    else {
                        if ($('.message_feed').length) {
                            $('.message_feed').remove();
                        }
                        var new_elem = $('<div class="message_feed"></div>').html(data.html);
                        $('.right_col').prepend(new_elem);
                    }
                    //autosize
                    $('#id_content').autosize(); 
                    //remove new color
                    $('#name_link_'+user_id).attr('style',''); 
                    $('#new_mess_'+user_id).hide(); 
                    //revert btn
                    $('#revert_btn').show();

                },
                error: function() {
                    alert('Unable to retrieve data.');
                    $('.right_col').removeClass("large_loader");
                    $('.right_col').html(old_data);
                }
            });  
}

$(document).ready(function() { 
        
    auto_complete();
    $('#id_content').autosize(); 

    $('#revert_btn').hide();

    $('#send_button').live('click',function() {
        /*$('#message_form').submit();*/
        /*$('#id_content').val('');*/

        url = "/messages/";

        if (window.location.pathname.indexOf('/lionface/') >= 0) 
        { 
            url = '/lionface' +  url;
        }

        $.ajax({
                type: 'POST',
                url: url,
                data: $('#message_form').serialize(), 
                success: function(data) {
                    console.log('ok');
                    var out = ($("#message_form", data).html());
                    var user_id = $('#id_user_id').val();
                    $("#message_form").html(out);
                    if ($('.success').length) {
                        $('.success').parent().remove();
                        load_messages(user_id);
                    }
                    else {
                        auto_complete();
                        $('#id_content').autosize(); 
                        if ($('.message_feed').length) {
                            $('#id_user_to').parent().parent().hide();
                        }
                    }


                    
                },
                error: function() {
                    console.log('fail');
                } 
            });
    });

    $('.message').click(function() {
        var meta = $(this).metadata();
        load_messages(meta.user);
    });

    $('#revert_btn').live('click',function() {
        if ($('.message_feed').length) {
            if ($(this).hasClass('desc')) {
                load_messages($('#id_user_id').val());
                $(this).removeClass('desc');
                }
            else {
                load_messages($('#id_user_id').val(),'desc');
                $(this).addClass('desc');
                }
            }
    });

})
