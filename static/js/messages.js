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

function change_form() {
    $('.big_form').hide()
    var new_form = '<tr> \
                        <td align="right" width="125">Message</td> \
                        <td align="left" width="455"> \
                            <textarea id="id_content" style="width: 100%; border: 1px solid #DDD;line-height: 1;" name="content"></textarea> \
                        </td> \
						<td align="right" width="50"><a href="javascript:;" id="send_button" class="send">Send</a></td> \
                    </tr>'

    $('.small_form').find('td :first').attr('width','125');
    $('.small_form').find('td :first').next().attr('width','455');
    $('.small_form').find('textarea').attr('style','width: 100%; border: 1px solid #DDD;line-height: 1;').removeAttr('rows').removeAttr('cols'); 
    if ($('.small_form').find('#send_button').length) {
    }
    else {
        $('.small_form').append('<td align="right" width="50"><a href="javascript:;" id="send_button" class="send">Send</a></td>');
    }
    $('.small_form').addClass('form_changed');
}

function load_messages(user_id, sort) {

        if (!(user_id)) {
            return;
            }

         if (!(sort)) {
            sort = '';
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
                    if (sort == 'desc' || data.sort == 'desc') {
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
                    //revert btn
                    $('#revert_btn').show();
                    //adding class if we have desc in db
                    if (data.sort == 'desc' && (!($('#revert_btn').hasClass('desc')))) {
                        $('#revert_btn').addClass('desc');
                    }
                    //change form
                    change_form();
                    //remove new color
                    $('#name_link_'+user_id).attr('style',''); 
                    $('#new_mess_'+user_id).hide(); 
                    //autosize
                    $('#id_content').autosize(); 
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

        make_request(url, $('#message_form').serialize(), function(data) {

                    var out = ($("#message_form", data).html());
                    var user_id = $('#id_user_id').val();
                    var check = $('.form_changed').length;
                    $("#message_form").html(out);
                    if ($('.success').length) {
                        $('.success').parent().remove();
                        load_messages(user_id);
                    }
                    else {
                        if (check) {
                            change_form();
                        }
                        auto_complete();
                        $('#id_content').autosize(); 
                        if ($('.message_feed').length) {
                            $('#id_user_to').parent().parent().hide();
                        }
                        alert("Message was not sent.");
                    }


                    
        });
    });

    $(document).on('click', '.message', function(e) {
        //getting element under cursor
        var starter = document.elementFromPoint(e.clientX, e.clientY);
        //used for proper linking in div
        if ($(starter).is('a')) {
            return
            }
        var meta = $(this).metadata();
        load_messages(meta.user);
    });

    $('#revert_btn').live('click',function() {
        if ($('.message_feed').length) {
            if ($(this).hasClass('desc')) {
                load_messages($('#id_user_id').val(),'asc');
                $(this).removeClass('desc');
                }
            else {
                load_messages($('#id_user_id').val(),'desc');
                $(this).addClass('desc');
                }
            }
    });

    $('.nav_link').live('click', function() { 
        url = $(this).attr('href');

        $.ajax({
                type: 'GET',
                url: url,
                success: function(data) {
                    $('.left_col').replaceWith(data);
                },
                error: function() {
                    console.log('fail');
                } 
            });

        return false;

    });

})
