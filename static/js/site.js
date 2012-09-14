//function for ajax POST requests
jQuery(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});              

function hookLinks() {
    // Friend links.
    $('.link-add-friend').unbind('click');
    $('.link-add-friend').click(function() {
        var data = $(this).metadata();
        var $this = $(this);
        if(data.user !== undefined) {
            $this.unbind('click');
            var $ohtml = $this.html();
            $this.append('<div class="link_loader"></div>');

            $.ajax('/account/friend/add/',{
                type: 'GET',
                data: 'user=' + encodeURIComponent(data.user),
                success: function(data) {
                    $this.html($ohtml);
                    if(data.status == 'OK') {
                        $this.html('Friend request sent.');
                    }
                },
                error: function() {
                    hookLinks();
                    $this.html($ohtml);
                }
            });
        }
        return false;
    });

    $('.link-remove-friend').unbind('click');
    $('.link-remove-friend').click(function() {
        var data = $(this).metadata();
        var $this = $(this);
        if(data.user !== undefined) {
            $this.unbind('click');
            var $ohtml = $this.html();
            $this.append('<div class="link_loader"></div>');

            $.ajax('/account/friend/remove/',{
                type: 'GET',
                data: 'user=' + encodeURIComponent(data.user),
                success: function(data) {
                    $this.html($ohtml);
                    if(data.status == 'OK') {
                        $this.html('Friend was removed.');
                    }
                },
                error: function() {
                    hookLinks();
                    $this.html($ohtml);
                }
            });
        }
        return false;
    });   

    $('.link-accept-friend').unbind('click');
    $('.link-accept-friend').click(function() {
        var data = $(this).metadata();
        var $this = $(this);
        if(data.request !== undefined) {
            $this.unbind('click');
            var $outElem = $this.closest('.link-output');
            var $ohtml = $outElem.html();
            $outElem.html('<div class="link_loader"></div>');
            $.ajax('/account/friend/accept/' + data.request + '/',{
                type: 'GET',
                success: function(data) {
                    $outElem.html($ohtml);
                    if(data.status == 'OK') {
                        $outElem.html('Friend request accepted.');
                    }
                },
                error: function() {
                    $outElem.html($ohtml);
                    hookLinks();
                }
            });
        }
        return false;
    });

    $('.link-decline-friend').unbind('click');
    $('.link-decline-friend').click(function() {
        var data = $(this).metadata();
        var $this = $(this);
        if(data.request !== undefined) {
            $this.unbind('click');
            var $outElem = $this.closest('.link-output');
            var $ohtml = $outElem.html();
            $outElem.html('<div class="link_loader"></div>');
            $.ajax('/account/friend/decline/' + data.request + '/',{
                type: 'GET',
                success: function(data) {
                    $outElem.html($ohtml);
                    if(data.status == 'OK') {
                        $outElem.html('Friend request declined.');
                    }
                },
                error: function() {
                    $outElem.html($ohtml);
                    hookLinks();
                }
            });
        }
        return false;
    });
}

$(function() {
    hookLinks();
});

function HideContent(d) {
    if(d.length < 1) { return; }
    document.getElementById(d).style.display = "none";
}
function ShowContent(d) {
    if(d.length < 1) { return; }
    document.getElementById(d).style.display = "block";
}
function ReverseContentDisplay(d) {
    if(d.length < 1) { return; }
    if(document.getElementById(d).style.display == "none") { document.getElementById(d).style.display = "block"; }
    else { document.getElementById(d).style.display = "none"; }
}       

function share_post(elem) { 
    url = "/posts/share/" + elem + "/";

    if (window.location.pathname.indexOf('lionface') >= 0) 
    { 
        url = '/lionface' +  url;
    }       

    $.ajax(url,
        {
            success: function(data) {
                alert("shared");
            },
            error: function() {
                alert('Unable to delete data.');
            }
        });    

}          

function del_post(elem) { 
    var data = $('.post_'+elem).metadata();
    url = "/posts/del/" + elem + "?user="+data.user;

    if (window.location.pathname.indexOf('lionface') >= 0) 
    { 
        url = '/lionface' +  url;
    }       

    $.ajax(url,
        {
            success: function(data) {
                $('.post_'+elem).prev('hr').hide()
                $('.post_'+elem).fadeOut()
            },
            error: function() {
                alert('Unable to delete data.');
            }
        });    

}       

function del_comm(elem) { 
    url = "/posts/dlcom/" + elem + "/";

    if (window.location.pathname.indexOf('lionface') >= 0) 
    { 
        url = '/lionface' +  url;
    }       

    $.ajax(url,
        {
            success: function(data) {
                if (data.status == 'removed') {
                    $('#comment_'+data.id).fadeOut();
                }
            },
            error: function() {
                alert('Unable to delete data.');
            }
        });    

} 

function post_comment(form_id, url) {
    $('#comment_form_'+form_id+' form input.submit-preview').remove();
    url = '/posts/test/'


    if (window.location.pathname.indexOf('lionface') >= 0) 
    { 
        url = '/lionface' +  url;
    }     

    $.ajax({
        type: "POST",
        data: $('#comment_form_'+form_id+' form').serialize(),
        url: url,
        success: function(html, textStatus) {
            /*$('#comment_form_'+form_id+' form').replaceWith(html.html);*/
            if ($('#comment_form_'+form_id).prev().find('.comment_list:last').length > 0) {
                $('#comment_form_'+form_id).prev().find('.comment_list:last').after(html.html);
            }
            else {
                $('#comment_form_'+form_id).prev().append(html.html);   
            }
            $('#comment_form_'+form_id+' form textarea').val('');
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            $('#comment_form_'+form_id+' form').replaceWith('Your comment was unable to be posted at this time.  We apologise for the inconvenience.');
        }

    });
}      

function check_for_messages(){
    url = '/check/messages/'

    if (window.location.pathname.indexOf('/lionface/') >= 0) 
    { 
        url = '/lionface' +  url;
    }     


    $.ajax(url,
            {
            success: function(data) {
                if (data.mess) {
                    if (parseInt(data.mess) > 0) {
                        if ($('#messages_id_notif').find('span').text() != data.mess) {
                            if ($('#messages_id_notif span').length) {
                                $('#messages_id_notif span').html(data.mess);
                                }
                            else {
                                $('#messages_id_notif').append('<span class="count">'+data.mess+'</span>');
                                }
                            }
                        }
                }
            },
            error: function() {
                console.log('fail');
            }
        });  

}

$(document).ready(function() {
    url = '/auto/';
    url_user = '/user/profile/'
    if (window.location.pathname.indexOf('/lionface/') >= 0) 
    { 
        url = '/lionface' +  url;
        url_user = '/lionface' +  url_user;
    }     
    $( "#search_input" ).autocomplete({
        source: url,
    }).keydown(function(e){
        if (e.keyCode === 13){
            console.log($(this).val());
            window.location = url_user + $(this).val();  
        }
    }).data( "autocomplete" )._renderItem = function( ul, item ) {
        return $( "<li></li>" )
        .data( "item.autocomplete", item )
        .append( "<a>" + item.label + '<div class="auto_subtext">' + item.value + '</div>' + "</a>" )
        .appendTo( ul );
    };

    //checking for new nofifications
    setInterval(function() {
        check_for_messages();
    }, 5000);




});

