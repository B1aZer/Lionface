$(document).ready(function() { 
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
        .append( "<a>" + item.label + '<div class="subtext">' + item.value + '</div>' + "</a>" )
        .appendTo( ul );
    };
    
    $('#send_button').click(function() {
        $('#message_form').submit();
        });

})
