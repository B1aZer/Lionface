/***** MAIN JS FILE (will load on every page) *****/

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

/** parents selector */
//$('.foo,.bar').filter(':parents(.baz)');
jQuery.expr[':'].parents = function(a,i,m){
    return jQuery(a).parents(m[3]).length < 1;
};


var process_request = false;
function make_request(input) {
    var url = input.url;
    var data = input.data || false;
    var callback = input.callback;
    var error_call = input.errorback || false;
    var type = input.type || false;
    var multi = input.multi || false;

    if (process_request && !multi) return;
    process_request = true;

    /*
    if (window.location.pathname.indexOf('/lionface/') >= 0)
    {
        url = '/lionface' +  url;
    }
    */

    if (data) {
        request_type = 'POST';
        }
    else {
        request_type = 'GET';
    }

    if (type) {
        request_type = type;
    }

    $.ajax(url,
        {
            type: request_type,
            data: data,
            success: function(data_success) {
                process_request = false;

                if ($.isFunction(callback)) {
                    callback(data_success);
                }

            },
            error: function() {
                process_request = false;
                console.log("error during request");
                if ($.isFunction(error_call)) {
                    error_call();
                }
            }
        });

}

function get_int(id) {
    if (!id) return;
    return id.replace( /^\D+/g, '')
}

function HideContent(d) {
    if(d.length < 1) { return; }
    if (document.getElementById(d)) {
        document.getElementById(d).style.display = "none";
    }
    else {
    }
}

function ShowContent(d) {
    if(d.length < 1) { return; }
    if (document.getElementById(d)) {
        document.getElementById(d).style.display = "block";
    }
    else {
    }
}

/** Make excerpts for news feed */
function make_excerpts() {
    var splitter = '<a href="#" class="excerpt">Show Entire Post</a>'
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

/** scrolling embed fix */
function fix_embed() {
    if ($('.post_content').length) {
        $('.post_content').each(function(i){
        if (!($(this).find('iframe').attr('scrolling'))) {
                $(this).find('iframe').attr('scrolling','no');
            }
        })
    }
}

/** django messages */
function create_message(message,type) {
    var type = type || 'warning';
    if (message) {
        var message = $('<li>', { 'class':type}).html(message);
        $('.messages').html(message);
    }
    else {
        $('.messages').html('');
    }
}

LionFace.Site = function() {
    this.runner();
}

LionFace.Site.prototype = {

    runner: function() {
        self_class = this;
        this.initialistaion();
        this.bind_public();
        this.page_members();
        if (!LionFace.User.is_anonymous) {
            this.bind_private();
        }
        this.attach_image_count = 0;
        this.MAX_UPLOAD_IMAGES = 21;
    },

    hookLinks: function() {
        // Friend links.
        $(document).on('click','.link-add-friend', function() {
            var data = $(this).metadata();
            var $this = $(this);
            if(data.user !== undefined) {
                $this.unbind('click');
                var $ohtml = $this.html();
                $this.append('<div class="link_loader" style="position: relative; left: -50px;"></div>');

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
                        $this.html($ohtml);
                    }
                });
            }
            return false;
        });

        $(document).on('click', '.link-remove-friend', function() {
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
                        $this.html($ohtml);
                    }
                });
            }
            return false;
        });

        $(document).on('click', '.link-accept-friend', function() {
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
                    }
                });
            }
            return false;
        });

        $(document).on('click','.link-decline-friend',function() {
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
                    }
                });
            }
            return false;
        });

        $(document).on('click', '.link-follow', function() {
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
                        }
                    },
                    error: function() {
                        $this.html($ohtml);
                    }
                });
            }
            return false;
        });

    },

    love_post: function(pk) {
        $item = $('#love_post_'+pk);
        $.ajax({
            url: '/posts/love/',
            data: {
                'pk': pk,
            },
            beforeSend: function(jqXHR, settings) {
                $item.fadeOut();
            },
            success: function(data, textStatus, jqXHR) {
                if (data.status == 'ok') {
                    $item.find('.post_love_count').html(data.count);
                    if (data.type == 'up') {
                        $item.find('a').html('Loved').css({
                            'color': $item.data('loved-color'),
                        });
                    } else if (data.type == 'down') {
                        $item.find('a').html('Love').css({
                            'color': $item.data('love-color'),
                        });
                    }
                }
            },
            complete: function(jqXHR, textStatus) {
                $item.fadeIn();
            },
        });
    },

    share_post: function (elem) {
        if (LionFace.User.is_anonymous) {
            return;
        }
        var url = "/posts/share/" + elem + "/";
        var meta = $('.post_'+elem).metadata();
        var post = $('.post_'+elem);

        if (post.find('.share_to').length) {
            var shared_div = post.find('.share_to');
            if (shared_div.is(":visible")) {
                var share_val = shared_div.find('.share_to_select').val();
                make_request({
                    url:url,
                    data:{
                        'post_type':meta.type,
                        'post_model':meta.model,
                        'share_to': share_val
                    },
                    callback: function(data) {
                        if (data.status == 'OK') {
                            $('.post_'+elem).find('.share_text').html('<span class="shared"> Shared </span>');
                            $('.post_'+elem).find('.share_text').show();
                            shared_div.hide();
                        }
                    }
                });
            }
            shared_div.show();
        }
        else {
            make_request({
                url:url,
                data:{
                    'post_type': meta.type,
                    'post_model': meta.model
                },
                callback: function(data) {
                    if (data.status == 'OK') {
                        $('.post_'+elem).find('.share_text').html('<span class="shared"> Shared </span>');
                        $('.post_'+elem).find('.share_text').show();
                    }
                }
            });
        }

    },

    del_post: function (elem) {
        if (LionFace.User.is_anonymous) {
            return;
        }
        var data = $('.post_'+elem).metadata();
        url = "/posts/del/" + elem + "?user="+data.user+"&type="+data.type+"&model="+data.model;
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
    },

    del_comm: function (elem) {
        if (LionFace.User.is_anonymous) {
            return
        }
        url = "/posts/dlcom/" + elem + "/";

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

    },

    post_comment: function (form_id, url) {
        if (LionFace.User.is_anonymous) {
            return
        }
        var event = $("#show-event-form").data('eventObj');
        var data = $('#comment_form_'+form_id+' form').serialize();
        $('#comment_form_'+form_id+' form input.submit-preview').remove();
        url = '/posts/test/'
        make_request({
            url: url,
            data: data,
            callback: function(html) {
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
            errorback: function () {
                $('#comment_form_'+form_id+' form').replaceWith('Your comment was unable to be posted at this time.  We apologise for the inconvenience.');
            }

        });
    },

    check_for_messages: function (){
        var url = '/check/messages/'
        make_request({
                url:url,
                multi:true,
                callback: function(data) {
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
                        else {
                            if ($('#messages_id_notif span').length) {
                                $('#messages_id_notif span').remove();
                            }
                        }
                    }
                },
                error_back: function() {
                    console.log('fail');
                }
            });

    },

    check_for_notifications: function (){
        var url = '/check/notifications/'

        make_request(
            {url:url, 
            multi:true,
            callback:function (data) {

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
                else {
                    if ($('#notifications_id_notif span').length) {
                        $('#notifications_id_notif span').remove();
                    }
                }

            }
        });
    },

    toggle_privacy: function (post_id, privacy) {
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
    },

    initialistaion: function() {
        this.hookLinks();
        /* Make excerpts here to prevent same function on all views without ajax */
        make_excerpts();
    },

    bind_private : function() {
        var _this = this;

        /******** FRIENDS **********/

        $(document).on('click','.link-unfollow',function(e) {
            e.preventDefault();
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
                            //this will fire only on news feed
                            if ($this.attr('class').indexOf('unfollow_feed') >= 0) {
                                $this.html('');
                                loadNewsFeed($("#news_feed"));
                            }
                            else {
                                $this.html('+ Follow');
                            $this.removeClass('link-unfollow');
                            $this.addClass('link-follow');
                            }
                        }
                    },
                    error: function() {
                        $this.html($ohtml);
                    }
                });
            }
            return false;
        });

        /** Autocomplete for search input */
        var url_auto = '/auto/';
        var url_user = '/';
        if ($("#search_input").length) {
            $( "#search_input" ).autocomplete({
                source: url_auto,
            }).keydown(function(e){
                if (e.keyCode === 13){
                    window.location = url_user + $(this).val();
                }
            }).data( "autocomplete" )._renderItem = function( ul, item ) {
                return $( "<li></li>" )
                .data( "item.autocomplete", item )
                .append( "<a>" + item.label + '<div class="auto_subtext">' + item.value + '</div>' + "</a>" )
                .appendTo( ul );
            };
        }

        /** Autocomplete for blocking users */
        var url_auto = '/auto/';
        $( "#block_user" ).autocomplete({
            source: url_auto,
        });

        //checking for new nofifications
        if (!LionFace.User.is_anonymous) {
            var self = this;
            setInterval(function() {
                self.check_for_messages();
                self.check_for_notifications();
            }, 20000);
        }

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
                                self_class.toggle_privacy(post_id,'Public')
                            }
                            else {
                                self.html('Friends');
                                self.attr('title','Privacy Settings: Friends Only');
                                self_class.toggle_privacy(post_id,'Friends')
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
        $(document).on('change', '.post_settings form :input', function(e) {
            var form_data = $(this).closest('form').serialize();
            var url = '/posts/change_settings/';
            var post = $(this).closest('.result');
            var meta = $(this).parents('.result').metadata();
            var post_id = post.attr("id").replace( /^\D+/g, '');
            data = "post_id="+post_id+"&post_type="+meta.type;
            if (form_data) { data = data + "&" + form_data; }
            make_request({
                url:url,
                data:data,
                callback:function(data_back) {
                    if (data_back.status == 'OK') {
                        if (data_back.privacy) {
                            _this.toggle_privacy(post_id, data_back.privacy);
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
                        if (data_back.loves) {
                            $('#love_post_'+post_id).hide();
                        }
                        else {
                            $('#love_post_'+post_id).show();
                        }
                        if (data_back.album || data_back.album === '') {
                            post.find('.album_name').html(data_back.album);
                            post.find('.album_name').attr('href',data_back.album_url);
                            if (data_back.album !== '') {
                                post.find('.album_name').show();
                            }
                            else {
                                post.find('.album_name').hide();
                            }
                        }
                    }
                }
            });
        });

        /** Hide users from feed */
        $(document).on('click','.hide_feed', function(e) {
            e.preventDefault();
            var self = $(this);
            var post = $(this).closest('.result');
            var meta = post.metadata();
            var url = '/account/hide/';
            make_request({
                url:url,
                data:{
                    user:meta.user,
                },
                callback: function() {
                    loadNewsFeed($("#news_feed"));
                }
            });
        });

        /** love button */
        $(document).on('click','.love_button',function(e) {
            e.preventDefault();
            var local_f = false;
            if (LionFace.User.page_id) {
                local_f = true;
            }
            var me = $(this);
            var url = '/pages/love_count/';
            var vote = 'up';
            var parent_div = me.parents('div[id^="page_"]');
            var page_id = get_int(parent_div.attr('id'));
            if (local_f) {
                page_id = LionFace.User.page_id;
            }
            var love_div = parent_div.find('.love_count');
            if (local_f) {
                love_div = $('.love_count');
            }
            var love_count = parseInt(love_div.html());
            if ($(this).hasClass('loved')) {
                vote = 'down';
            }
                make_request({
                    url:url,
                    data: {
                        'vote': vote,
                        'page_id': page_id,
                    },
                    callback: function(data) {
                        if (data.status == 'OK') {
                            if (vote == 'up') {
                                if (me.find('.loves_icon').length) {
                                    me.find('span').html('Loved');
                                }
                                else {
                                    me.html('Loved');
                                }
                                me.addClass('loved');
                                if (data.loved || data.loved == 0) {
                                    love_count = parseInt(data.loved);
                                }
                                else {
                                    love_count = love_count + 1;
                                }

                            }
                            else {
                                if (me.find('.loves_icon').length) {
                                    me.find('span').html('Love');
                                }
                                else {
                                    me.html('Love');
                                }
                                me.removeClass('loved');
                                if (data.loved || data.loved == 0) {
                                    love_count = parseInt(data.loved);
                                }
                                else {
                                    love_count = love_count - 1;
                                }
                            }
                            love_div.html(love_count);
                        }
                    }
                });
        });

    },

    attach_image: function(event) {
        var _this = this;
        event.preventDefault();
        if (_this.attach_image_count > _this.MAX_UPLOAD_IMAGES) {
            create_message("Too many images", "error");
            return;
        }
        var $attached_images = $('#attached-images');
        $attached_images.find("ul").append("<li class='attached_image_class'><input class='attach-image-file' type='file' name='image' style='display: none;'/><input class='attach-image-rotation' type='text' name='image_rotation' style='display: none;'/></li>");
        // document.getElementsByClassName('attach-image-file')[0].addEventListener('change', uploadImage, false);
        $attached_images.find('.error-list').remove();

        $(".attach-image-file").on("change", function(e) {
            // check uploaded image size
            if(e.target.files[0].size > 5242880) {
                $attached_images.find("ul li").last().html('');
                if ($attached_images.find('.error-list').length) {
                    var $errors = $attached_images.find('.error-list');
                }
                else {
                    $attached_images.append('<ul class="error-list"></ul>');
                    var $errors = $attached_images.find('.error-list');
                }
                $errors.append('<li>Image is larger than 5mb<li>');
                return; 
            }
            var orientation = '';
            var image = e.target.files[0];
            var fr   = new FileReader;
            fr.readAsBinaryString(image);

            fr.onloadend = function() {
                    var exif = EXIF.readFromBinaryFile(new BinaryFile(this.result));
                    orientation = exif.Orientation;

                    if (image === undefined) {
                        console.log('file not select');
                        $attached_images.find('ul li').last().remove();
                        return;
                    }
                    if ($.inArray(image.type,['image/jpeg','image/png']) < 0) {
                        console.log(image.type);
                        $attached_images.find('ul li').last().remove();
                        return;
                    }
                    window.loadImage(
                        image,
                        function (img) {
                            var $li = $attached_images.find('ul li').last();
                            $li.attr('id', 'img-' + _this.attach_image_count);
                            $li = $attached_images.find('#img-' + _this.attach_image_count);
                            //<a href='#' class='attached_image_full_size' id='fullsize' style='float: left;' title='Make full-size in the post'>+</a> \
                            $li.append(" \
                            <div id='image_settings' class='feed image_settings_class'> \
                                <a href='#' class='attached_image_left' id='image-rotate-left' title='Rotate Image Left'></a> \
                                <a href='#' class='attached_image_right' id='image-rotate-right' title='Rotate Image Right'></a> \
                                <a href='#' class='attached_image_delete' id='delete' style='float: right;' title='Remove Photo'>x</a> \
                            </div> \
                            ");
                            $li.append(img);
                            _this.attach_image_count += 1;
                            $li.find('.attach-image-rotation').val('0');

                            $image_settings = $li.find('#image_settings');
                            $image_settings.width(img.width);
                            if ($image_settings.length != 1)
                                return;
                            $image_settings.hide();
                        },
                        {
                            canvas: true,
                            orientation: orientation,
                            maxWidth: 190,
                            /*minWidth: 190,*/
                        }
                    );
            };
            

            
        });
        $attached_images.find(".attach-image-file:last").click();
    },

    attach_dropped_image: function (e) {
        //console.log('1');
        var $attached_images = $('#attached-images');
        e = e.originalEvent;
        e.preventDefault();
        var image = (e.dataTransfer || e.target).files[0];
        //console.log(image);
        window.loadImage(
            image,
            function (img) {
                $attached_images.find('ul').append(img);
                var data = {
                    image: image
                };
                // $.post('/posts/save/', data, function (data) {
                //     alert('hi');
                // }, 'JSON');
                //console.log(img);
            },
            {
                maxWidth: 190
            }
        );
    },

    revert_textbox_height : function () {
        $('.postbox_textarea').height(30);
        $('#postboxbutton').height(12);
    },

    bind_public : function() {
        
        var _this = this;

        //Switch search queries
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


        /** toggle post subtext */
        $(document).on('mouseover','.result',function() {
        var meta = $(this).metadata();
        if (meta.type != 'friend post' && meta.postid) {
            ShowContent(meta.postid);
        }
        });

        $(document).on('mouseout','.result',function() {
        var meta = $(this).metadata();
        if (meta.type != 'friend post' && meta.postid) {
            HideContent(meta.postid);
        }
        });

        /** Follow post. */
        $(document).on('click','.follow_post', function(e) {
            e.preventDefault();
        });

        /** comments pagination */
        $(document).on('click','.coomments_see_more', function(e) {
            e.preventDefault();
            var self = $(this);
            var url = self.attr('href');
            make_request({
                url:url,
                callback: function(data) {
                    if (data.status == 'OK') {
                        self.siblings('#comments').prepend(data.html);
                        self.remove();
                    }
                }
            });
        });

        /** search/related mutual friend toogle */
        $(document).on('click','.mutual_friends',function() {
            if ($(this).data('toggled')) {
                $(this).find('.mutual_friend_list').hide();
                $(this).data('toggled', false);
            }
            else {
                $(this).find('.mutual_friend_list').show();
                $(this).data('toggled', true);
            }
        });

        /** attached images */
        $('.pending_images').sortable();

        $(document).on('mouseenter', '.attached_image_class', function() {
            $(this).find('.image_settings_class').show();
        });

        $(document).on('mouseleave', '.attached_image_class', function() {
            $(this).find('.image_settings_class').hide();
        });

        $(document).on('click', '.attached_image_full_size', function(e) {
            e.preventDefault();
        });

        $(document).on('click', '.attached_image_delete', function(e) {
            e.preventDefault();            
            var image = $(this).parents('.attached_image_class')
            image.fadeOut( function() { 
                $(this).remove();
            });
        });

        /** image rotation using css */
        $(document).on('click', '.attached_image_left', function(e) {
            e.preventDefault();            
            /*
            var image = $(this).parents('.attached_image_class').find('img').attr('src');
            if (!image) return;
            var raph = Raphael($(this).parents('#image_settings')[0]);
            var img = raph.image(image);
            var angle = 0;
            angle = angle - 90;
            img.stop().animate({transform: "r" + angle}, 1000, "<>");
            */
            if ($(this).parents('.attached_image_class').find('img').length ) {
                var image = $(this).parents('.attached_image_class').find('img');
            }
            else {
                var image = $(this).parents('.attached_image_class').find('canvas');
            }
            var input = $(this).parents('.attached_image_class').find('.attach-image-rotation');
            var angle = parseInt(input.val());
            if (!image) return;
            cfangle = angle * 90 - 90;
            ieangle = angle - 1;
            image.attr('style','-webkit-transform: rotate(' + cfangle + 'deg);\
                                -moz-transform: rotate(' + cfangle + 'deg); \
                                filter: progid:DXImageTransform.Microsoft.BasicImage(rotation=' + ieangle + ');'); 
            input.val(ieangle);
        });

        $(document).on('click', '.attached_image_right', function(e) {
            e.preventDefault();            
            if ($(this).parents('.attached_image_class').find('img').length ) {
                var image = $(this).parents('.attached_image_class').find('img');
            }
            else {
                var image = $(this).parents('.attached_image_class').find('canvas');
            }
            var input = $(this).parents('.attached_image_class').find('.attach-image-rotation');
            var angle = parseInt(input.val());
            if (!image) return;
            cfangle = angle * 90 + 90;
            ieangle = angle + 1;
            image.attr('style','-webkit-transform: rotate(' + cfangle + 'deg);\
                                -moz-transform: rotate(' + cfangle + 'deg); \
                                filter: progid:DXImageTransform.Microsoft.BasicImage(rotation=' + ieangle + ');'); 
            input.val(ieangle);
        });

        /* remove all blank attachments */
        $(document).on('click', '.attaching_class', function (e) {
            $('.attached_image_class').each( function (i,e) {
                    if (!$(e).attr('id')) {;
                        $(e).remove();
                    }
            });
            _this.attach_image(e);
        });

        /** loved user list */
        $(document).on('click', '.post_love_count', function() {
            if ($(this).data('toggled')) {
                $(this).parents('.subtext').find('.loved_users_list').hide();
                $(this).data('toggled', false);
            }
            else {
                $(this).parents('.subtext').find('.loved_users_list').show();
                $(this).data('toggled', true);
            }
        });
        
    },
    page_members : function () {
        /** PAGE MEMBERS CHAOS */
        var volunteer_flag=false;
        var intern_flag=false;
        var employee_flag=false;
        var edit_member_url;

        $(document).on('click','.edit_member', function(e) {
            edit_member_url = $(this).attr('href');
        });

        $(document).on('click','#volunteer_flag', function(e) {
            volunteer_flag = true;
            intern_flag = false;
            employee_flag = false;
        });

        $(document).on('click','#intern_flag', function(e) {
            volunteer_flag = false;
            intern_flag = true;
            employee_flag = false;
        });

        $(document).on('click','#employee_flag', function(e) {
            volunteer_flag = false;
            intern_flag = false;
            employee_flag = true;
        });

        $(document).on('click','.save_member', function(e) {
            create_message();
            var monthtext=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sept','Oct','Nov','Dec'];
            var member_type = false;
            var url = $(this).attr('href');
            if (edit_member_url) {
                url = edit_member_url;
            }
            if (volunteer_flag) { member_type = 'VL'; }
            if (intern_flag) { member_type = 'IN'; }
            if (employee_flag) { member_type = 'EM'; }
            var from_date_month = $(this).parent().find('.former_member.month_select').val() || $(this).parent().find('.current_member.month_select').val();
            var from_date_year = $(this).parent().find('.former_member.year_select').val() || $(this).parent().find('.current_member.year_select').val();
            from_date_month = monthtext.indexOf(from_date_month) + 1;
            var from_date = from_date_month + '/' + from_date_year;
            var to_date_month = $(this).parent().find('.date_to.month_select').val();
            var to_date_year = $(this).parent().find('.date_to.year_select').val();
            to_date_month = monthtext.indexOf(to_date_month) + 1;
            if (to_date_year && to_date_month) {
                var to_date = to_date_month + '/' + to_date_year;
            }
            else {
                var to_date = '';
            }
            var from_date_former = $(this).parent().find('.former_member');
            var from_date_current = $(this).parent().find('.current_member');
            var to_date_form = $(this).parent().find('.date_to');
            if (member_type && from_date) {
                make_request({
                    url:url,
                    data: {
                        'member_type':member_type,
                        'from_date':from_date,
                        'to_date':to_date,
                    },
                    callback: function (data) {
                        if(data.status=='OK') {
                            if (data.redirect) {
                                if ($('#page_members_id').length) {
                                    $('#page_members_id').html(data.html);
                                    /*from_date_former.val('') */
                                    /*from_date_current.val('');*/
                                    /*to_date_form.val('');*/
                                }
                                else {
                                    history.go(0);
                                }
                            }
                            else {
                                create_message('Member saved','success');
                                /*$('.former_member').val('')*/
                                /*$('.current_member').val('');*/
                            }
                        }
                        else if (data.message) {
                            create_message(data.message);
                        }
                        else {
                            create_message('Error during saving','error');
                            /*from_date_former.val('');*/
                            /*from_date_current.val('');*/
                            /*to_date_form.val('');*/
                        }
                    }
                });
            }

        });


        $(document).on('click','#remove_member', function(e) {
            if (edit_member_url) {
                make_request({
                    url:edit_member_url,
                    data: {
                        'delete':true,
                    },
                    callback: function(data) {
                        if (data.status == 'OK') {
                            $('#member_' + data.id).remove();
                        }
                    }
                });
            }
        });

    },
    /* day month year selects */
    daydatedropdown : function(dayfield, monthfield, yearfield, day, month, year){
        /* usage LionFace.Site.daydatedropdown('birth_day_select','birth_month_select','birth_year_select'); */
        var monthtext=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        var today=new Date()
        var dayfield=$('.'+dayfield);
        var monthfield=$('.'+monthfield);
        var yearfield=$('.'+yearfield);
        if (day) {
            var day_tm = day - 1 ;
        }
        else {
            var day_tm = today.getDate() - 1 ;
        }
        var day_t = day || today.getDate()
        if (month >= 0 ) {
            var month_t = month;
        }
        else {
            var month_t = today.getMonth();
        }
        var year_t = year || today.getFullYear();

        dayfield.each(function() {
            var day = $(this).get(0);
            for (var i=0; i<31; i++) day.options[i]=new Option(i+1, i+1)
            day.options[day_tm]=new Option(day_t, day_t, true, true) 
        });
        
        monthfield.each(function() {
            var month = $(this).get(0);
            for (var m=0; m<12; m++) month.options[m]=new Option(monthtext[m], monthtext[m])
            month.options[month_t]=new Option(monthtext[month_t], monthtext[month_t], true, true)
        });

        yearfield.each(function() {
            var year = $(this).get(0);
            var thisyear=today.getFullYear();
            for (var y=0; y<90; y++){
                year.options[y]=new Option(thisyear, thisyear)
                thisyear-=1
            }
            year.options[0]=new Option(year_t, year_t, true, true)
        })
    },
    /* month year selects */
    datedropdown : function(monthfield, yearfield){
        var monthtext=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        var today=new Date()
        var monthfield=$('.'+monthfield);
        var yearfield=$('.'+yearfield);
        monthfield.each(function() {
            var month = $(this).get(0);
            for (var m=0; m<12; m++) month.options[m]=new Option(monthtext[m], monthtext[m])
            month.options[today.getMonth()]=new Option(monthtext[today.getMonth()], monthtext[today.getMonth()], true, true)
        });

        yearfield.each(function() {
            var year = $(this).get(0);
            var thisyear=today.getFullYear();
            for (var y=0; y<80; y++){
                year.options[y]=new Option(thisyear, thisyear)
                thisyear-=1
            }
            year.options[0]=new Option(today.getFullYear(), today.getFullYear(), true, true)
        })
    }
}

$(function() {
    LionFace.Site = new LionFace.Site();
});
