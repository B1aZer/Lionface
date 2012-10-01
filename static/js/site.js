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

function make_request(input) {
    var url = input.url;
    var data = input.data || false;
    var callback = input.callback;
    var error_call = input.errorback || false;

    if (window.location.pathname.indexOf('/lionface/') >= 0) 
    { 
        url = '/lionface' +  url;
    }   

    if (data) {
        request_type = 'POST';
        }
    else {
        request_type = 'GET';
    }

    $.ajax(url,
        {
            type: request_type, 
            data: data,
            success: function(data_success) {

                if ($.isFunction(callback)) {
                    callback(data_success);
                }
            
            },
            error: function() {
                console.log("error during request");
                if ($.isFunction(error_call)) {
                    error_call();
                }  
            }
        });

}

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

    $('.link-follow').unbind('click');
    $('.link-follow').click(function() {
        var data = $(this).metadata();
        var $this = $(this);
        if(data.user !== undefined) {
            $this.unbind('click');
            var $ohtml = $this.html();
            $this.append('<div class="link_loader"></div>');

            $.ajax('/account/follow/',{
                type: 'GET',
                data: 'user=' + encodeURIComponent(data.user),
                success: function(data) {
                    $this.html($ohtml);
                    if(data.status == 'OK') {
                        $this.html('- Unfollow');
                        $this.removeClass('link-follow');
                        $this.addClass('link-unfollow');
                        hookLinks();
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

    $('.link-unfollow').unbind('click');
    $('.link-unfollow').click(function() {
        var data = $(this).metadata();
        var $this = $(this);
        if(data.user !== undefined) {
            $this.unbind('click');
            var $ohtml = $this.html();
            $this.append('<div class="link_loader"></div>');

            $.ajax('/account/unfollow/',{
                type: 'GET',
                data: 'user=' + encodeURIComponent(data.user),
                success: function(data) {
                    $this.html($ohtml);
                    if(data.status == 'OK') {
                        $this.html('+ Follow');
                        $this.removeClass('link-unfollow');
                        $this.addClass('link-follow');
                        hookLinks();
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
}

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
    make_request({
        url:url,
        callback: function(data) {
            if (data.status == 'OK') {
                $('.post_'+elem).find('.share_text').html('<p> Shared. </p>');
                $('.post_'+elem).find('.share_text').show();
            }
        }
    });    

}          

function del_post(elem) { 
    var data = $('.post_'+elem).metadata();
    url = "/posts/del/" + elem + "?user="+data.user+"&type="+data.type;
    make_request({
        url:url,
        callback:function(post_data) 
        {
            if (post_data.status == 'OK') {
                $('.post_'+elem).prev('hr').hide();
                $('.post_'+elem).fadeOut();
            }
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
            if ($('#comment_form_'+form_id).closest('.comment_container').find('.comment_list:last').length) {
                $('#comment_form_'+form_id).closest('.comment_container').find('.comment_list:last').after(html.html);
            }
            else {
                $('#comment_form_'+form_id).closest('.comment_container').find('#comments').append(html.html);   
            }
            $('#comment_form_'+form_id+' form textarea').val('');
            /** following mark */
            $('#comment_form_'+form_id).closest('.result').find('.follow_post').html('Unfollow');

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

function check_for_notifications(){
    url = '/check/notifications/'

    make_request(
        {url:url, callback:function (data) {

            if (parseInt(data.notfs) > 0) {
                if ($('#notifications_id_notif').find('span').text() != data.notfs) {
                    if ($('#notifications_id_notif span').length) {
                        $('#notifications_id_notif span').html(data.notfs);
                    }
                    else {
                        $('#notifications_id_notif').append('<span class="count">'+data.notfs+'</span>');
                    }
                }
            }
    
        }
    });
} 

function toggle_privacy(post_id, privacy) {
    var post = $('#post_'+post_id)
    if (post.length) {
        var settings_privacy = post.find('.post_settings select[name=privacy_settings]').val();
        var post_privacy = post.find('.toggle_privacy').html();
        if (post_privacy != privacy) {
            post.find('.toggle_privacy').html(privacy);
        }
        if (settings_privacy != privacy) {
            post.find('.post_settings select[name=privacy_settings]').val(privacy)
        }
    }
}

/** Make excerpts for news feed */
function make_excerpts() {
    var splitter = '<a href="#" class="excerpt">show more</a>'
    if ($('.result').length) {
        $('.result').each(function (index) {
            if ($(this).find('.excerpt').length) {
                var content = $(this).find('.post_content').html();
                content = content.split(splitter);
                html_before = content[0]
                html_after = content[1]
                //remove <br> from beggining
                html_after = html_after.replace(/^<br>/g, '')
                /*console.log(content);*/
                $(this).find('.post_content').html(html_before).append(splitter).append('<div class="full_post" style="display:none">' + html_after + '</div>');
            }
        });
    }
}     

$(document).ready(function() {
    hookLinks();

    //Swith search queries
    $('#quick_search').submit(function() {
        if ( $(this).find('#search_input').val().indexOf( "#" ) !== -1 ) {
            var tag=$(this).find('#search_input').val().split(' ');
            tag = tag[0].replace('#','');
            url = '/tag/?models=tags_tag&q='+tag;
            window.location = url;
            return false;
        }
    })

    //Toggle comments
    $(document).on('click','.toggle_comments', function(e) {
        e.preventDefault();
        var post_id = $(this).parents('.result').metadata().postid;
        var toggled = $(this).data('toggled');
        $(this).data('toggled', !toggled);
        if (!toggled) {
            $('.comment_'+post_id).show(function() {
                $('.text_comment').autosize();
            });
        }
        else {
            $('.comment_'+post_id).hide(); 
        }
    });

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
        check_for_notifications();
    }, 20000);

    /** Change privacy settings for content posts */
    $(document).on('click','.toggle_privacy', function() {
        var self = $(this);
        var post = $(this).parents('.result');
        var data = $(this).parents('.result').metadata();
        var post_type = 'F';
        if ($(this).html() == 'Public') {
            post_type = 'P';
        }

        if (data.type == "content post") {
            var post_id = post.attr("id").replace( /^\D+/g, '');
            var send_data = {'post_id':post_id,'type':post_type};
            url = '/posts/toggle_privacy/';
            make_request({
                url:url,
                data:send_data,
                callback:function (data_back) {
                    if (data_back.status == 'OK') {
                        if (post_type == 'F') {
                            self.html('Public');
                            self.attr('title','Privacy Settings: Public');
                            toggle_privacy(post_id,'Public')
                        }
                        else {
                            self.html('Friends');
                            self.attr('title','Privacy Settings: Friends Only');
                            toggle_privacy(post_id,'Friends')
                        }
                    }
                }
            });
        }
    });

    /** Follow post. */
    $(document).on('click','.follow_post', function(e) {
        
        e.preventDefault();
        var self = $(this);
        var value = self.html();
        var post = $(this).parents('.result');
        var data = $(this).parents('.result').metadata();
        var post_id = post.attr("id").replace( /^\D+/g, '');
        var send_data = {'post_id':post_id,'post_type':data.type,'value':value};
        url = '/posts/follow/';
        make_request({
            url:url,
            data:send_data,
            callback:function (data_back) {
                if (data_back.status == 'OK') {
                    if (value == 'Unfollow') {
                        self.html('Follow');
                    }
                    else {
                        self.html('Unfollow');
                    }
                }
                else {
                    alert(data_back.html);
                }
            }
        });   
    });

    /** Displaying post settings */
    $(document).on('click','.toggle_settings', function(e) {
        e.preventDefault();
        if (!($(this).data('toggled'))) {
            $(this).closest('.subtext').find('.post_settings').show();
            $(this).data('toggled',true);
        }
        else {
            $(this).closest('.subtext').find('.post_settings').hide();
            $(this).data('toggled',false);
        }
    });

    /** Post settings. */
    $(document).on('change','.post_settings form :input', function(e) {
        var form_data = $(this).closest('form').serialize();
        var url = '/posts/change_settings/'
        var post = $(this).closest('.result');
        var meta = $(this).parents('.result').metadata();
        var post_id = post.attr("id").replace( /^\D+/g, '');
        data = "post_id="+post_id+"&post_type="+meta.type
        if (form_data) { data = data + "&" + form_data; } 
        make_request({
            url:url,
            data:data,
            callback:function(data_back) {
                if (data_back.status == 'OK') {
                    if (data_back.privacy) {
                        toggle_privacy(post_id, data_back.privacy);
                    }
                    if (data_back.commenting) {
                        $('#hide_comment_link_'+post_id).hide();
                        $('#hide_follow_link_'+post_id).hide();
                        $('#hide_comment_'+post_id).hide();
                    }
                    else {
                        $('#hide_comment_link_'+post_id).show();
                        $('#hide_follow_link_'+post_id).show();
                        $('#hide_comment_'+post_id).show();
                    }  
                    if (data_back.sharing) {
                        $('#hide_share_'+post_id).hide();
                    }
                    else {
                        $('#hide_share_'+post_id).show();
                    }
                }
            }
        });
    });

    /** Show full post */
    $(document).on('click','.excerpt', function(e) {
        e.preventDefault();
        var self = $(this);
        var post_content = $(this).parent();
        if (post_content.find('.full_post').length) {
            var html_after = post_content.find('.full_post').html();
            post_content.find('.full_post').show();
            /*post_content.append(html_after);*/
            self.hide();
            post_content.append('<a href="#" class="show_less">Hide</a>');
        }
    });

    /** Show excerpt from post */
    $(document).on('click','.show_less', function(e) {
        e.preventDefault();
        var self = $(this);
        var post_content = $(this).parent();
        post_content.find('.full_post').hide(); 
        post_content.find('.excerpt').show(); 
        self.remove();
    });
    

});

