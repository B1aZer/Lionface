function auto_complete() {

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
        .append( "<a>" + item.label + '<div class="subtext">' + item.value + '</div>' + "</a>" )
        .appendTo( ul );
    };    

}

$(document).ready(function() { 
    url = '/auto/';
    if (window.location.pathname.indexOf('/lionface/') >= 0) 
    { 
        url = '/lionface' +  url;
        url_user = '/lionface' +  url_user;
    }     
    
    auto_complete();

    $('#send_button').click(function() {
        $('#message_form').submit();
    });

    $('.message').click(function() {
        url = "/messages/show/";

        if (window.location.pathname.indexOf('/lionface/') >= 0) 
        { 
            url = '/lionface' +  url;
        }  
        if (!($('.message_feed').length)) {
            var elem = $('<div class="message_feed"></div>');
            $('.right_col').prepend(elem);
        }
        else {
        }

        var meta = $(this).metadata();
        //TODO:autocomplete
        $('#id_user_to').autocomplete("destroy");
        
        //loading
        var old_data = $('.right_col').html();
        $('.right_col').html('');
        $('.right_col').addClass("large_loader");

        $.ajax({
                type: 'POST',
                url: url,
                data: {
                    user_id : meta.user,
                },
                success: function(data) {
                    $('.right_col').removeClass("large_loader");
                    $('.right_col').html(old_data);
                    $('.message_feed').html(data.html);
                    //autocomplete
                    auto_complete();

                },
                error: function() {
                    alert('Unable to retrieve data.');
                    $('.right_col').removeClass("large_loader");
                    $('.right_col').html(old_data);
                }
            });  
    });

})
