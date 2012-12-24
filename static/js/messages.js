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

function load_messages(user_id, sort, page, incolumn) {

        if (!(user_id)) {
            return;
        }

        if (!(page)) {
            if ($('body').data('messages')) {
                page = $('body').data('messages').page;
            }
            else {
                page = 1;
            }

        }

        if (!(sort)) {
            sort = '';
        } 

        if (!(incolumn)) {
            //Appending to current feed
            incolumn = false;
        }   

        //saving some values
        $('body').data('messages', { user_id: user_id, sort: sort, page: page });

        url = "show/";

        if (window.location.pathname.indexOf('/lionface/') >= 0) 
        { 
            url = '/lionface' +  url;
        }  
        
        //loading
        if (!(incolumn)) {
            var old_data = $('.right_col').html();
            $('.right_col').html('');
            $('.right_col').addClass("large_loader");
        }

        $.ajax({
                type: 'POST',
                url: url,
                data: {
                    user_id : user_id,
                    sort : sort,
                    page : page
                },
                success: function(data) {
                    if (!(incolumn)) {  
                        //remove loading
                        $('.right_col').removeClass("large_loader");
                        //old html
                        $('.right_col').html(old_data);
                    }
                    //saving old messages button
                    var old_btn = $('#show_older').clone();
                    //remove To input
                    $('#id_user_to').parent().parent().hide();
                    //input user id
                    $( "#id_user_id" ).val( user_id );
                    //populate feed
                    if (sort == 'desc' || data.sort == 'desc') {
                        //postbox on top
                        if ($('.message_feed').length && !incolumn) {
                            $('.message_feed').remove();
                        }
                        if (!incolumn) {
                            var new_elem = $('<div class="message_feed"></div>').html(data.html);
                            $('.right_col').append(new_elem);
                        }
                        else {
                            if ($('.message_feed').length) {
                                $('.message_feed').append(data.html);
                            }
                        }
                        //show older
                        $('#show_older').remove();
                        $('.mess :last').after(old_btn);
                        old_btn.addClass('bottom');
                    }
                    else {
                        if ($('.message_feed').length && !incolumn) {
                            $('.message_feed').remove();
                        }
                        if (!incolumn) {
                            var new_elem = $('<div class="message_feed"></div>').html(data.html);
                            $('.right_col').prepend(new_elem);
                        }
                        else {
                            if ($('.message_feed').length) {
                                $('.message_feed').prepend(data.html);
                            }
                        } 
                        //older btn
                        $('#show_older').remove();
                        $('.mess :first').before(old_btn);
                        old_btn.removeClass('bottom'); 
                    }
                    //revert btn
                    $('#revert_btn').show();
                    //updating messages count
                    $('.user_id_'+user_id).find('.ms').html(data.ms+"s");
                    $('.user_id_'+user_id).find('.mr').html(data.mr+"r");
                    $('.user_id_'+user_id).find('.tm').html(parseInt(data.mr)+parseInt(data.ms)+"m");
                    //adding class if we have desc in db
                    if (data.sort == 'desc' && (!($('#revert_btn').hasClass('desc')))) {
                        $('#revert_btn').addClass('desc');
                    }
                    //change form
                    change_form();
                    //remove new color
                    $('#name_link_'+user_id).attr('style',''); 
                    $('#new_mess_'+user_id).remove(); 
                    //nullify new mess count
                    if ((!($('.new_flag').length)) && $('#messages_id_notif span').length) {
                        $('#messages_id_notif').find('span').remove();
                    }
                    //autosize
                    $('#id_content').autosize(); 
                    //scroll to last message
                    if (!(incolumn)) {  
                        if (sort == 'desc' || data.sort == 'desc') {}
                        else {
                            if ($('.mess :last').length) {
                                if (window.innerHeight <= $('.mess :last').offset().top) {
                                    $('html, body').animate({
                                             scrollTop: $('.mess :last').offset().top,
                                         }, 500);
                                }
                            }
                        }
                    }
                    //overwriting some values
                    $('body').data('messages').page = data.page;
                    $('body').data('messages').nextpage = data.nextpage;
                    //older btn
                    if ($('body').data('messages').nextpage != $('body').data('messages').page) {
                        $('#show_older').show();
                    }
                    else {
                        $('#show_older').hide();
                    }
                },
                error: function() {
                    alert('Unable to retrieve data.');
                    if (!(incolumn)) { 
                        $('.right_col').removeClass("large_loader");
                        $('.right_col').html(old_data);
                    }
                }
            });  
}

function reset_message_count() {
    if ($('#messages_id_notif span').length) {
        $('#messages_id_notif span').remove();
    }
}

$(document).ready(function() { 
        
    auto_complete();
    $('#id_content').autosize(); 

    $('#revert_btn').hide();
    $('#show_older').hide();

    $('#send_button').live('click',function() {
        /*$('#message_form').submit();*/
        /*$('#id_content').val('');*/

        url = ".";

        make_request({url:url, data:$('#message_form').serialize(), callback:function(data) {

                    var out = ($("#message_form", data).html());
                    var user_id = $('#id_user_id').val();
                    var check = $('.form_changed').length;
                    $("#message_form").html(out);
                    if ($('.success').length) {
                        $('.success').parent().remove();
                        load_messages(user_id,false,1);
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
                }
        });
    });

    $(document).on('click', '.message', function(e) {
        //getting element under cursor
        var starter = document.elementFromPoint(e.clientX, e.clientY);
        var self = $(this);
        //used for proper linking in div
        if ($(starter).is('a') || $(starter).hasClass('message_thumbnail')) {
            return
            }
        $('.active_message').removeClass('active_message');
        self.addClass('active_message');
        var meta = $(this).metadata();
        load_messages(meta.user,false,1);
    });

    $('#revert_btn').live('click',function(e) {
        e.preventDefault();
        if ($('.message_feed').length) {
            if ($('body').data('messages').page) {
                var page_num = $('body').data('messages').page;
            }else{
                page_num = false;
            }
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

    $(document).on('click', '#show_older', function(e) { 
        e.preventDefault();
        if ($('body').data('messages').nextpage != $('body').data('messages').page) {
            load_messages($('body').data('messages').user_id,false,$('body').data('messages').nextpage,true);
        }
    });

    reset_message_count();

})
