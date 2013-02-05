LionFace.Chat = function(options) {
    this.options = $.extend({
        
    }, options || {});;
    this.init();
};


LionFace.Chat.prototype = {

    init : function() {
        var me = this;
        me.bind_chat();
    },

    bind_chat : function() {

        var cont_width = 234;
        var socket = io.connect("/chat");
        var connected = false;
        auto_size();

        var source   = $("#message-template").html();
        var template = Handlebars.compile(source);
        
        source = $("#message-template-noreply").html();
        var template2 = Handlebars.compile(source);

        function auto_size() {
            $('.chat_enter').autosize({ 
                callback: function(ta, height) {
                    if (ta > 60) {
                        $(this).css({'overflow-y':'auto'});
                        return false;
                    }
                    else {
                        //var parent_mh = parseInt($(this).siblings('.message_content').css('max-height'));
                        var parent_mh = 230;
                        parent_mh = parent_mh - ta + 16;
                        $(this).siblings('.message_content').css('max-height',parent_mh+'px');
                        return true;
                    }
                }
            });
        }

        function toggle_tabs() {
            var tabs = tabs || $('.chat_div');
            tabs.each( function (i,e) {
                if ($(e).hasClass('tab_opened')) {
                    var username = $(e).attr('id').replace('name_','');
                    $('#message_' + username).show();
                    $(e).data('toggled',true);
                    // left position
                                var count = i;
                                var opnind = $(e).index('.tab_opened');
                                var opened_count = $('.tab_opened:lt('+opnind+')').length;
                                count = count - opened_count;
                                //var left = (cont_width + 16 + 5) * count + 210;
                                var left = (cont_width - 50 + 16 + 5) * count + (cont_width + 16 + 5) * opened_count + 210;
                                $('#message_'+username).css('left',left);

                    // width
                    $(e).width(cont_width);
                                
                    // scroll
                    var last_el = $('#message_' + username).find('div:last')
                    if (last_el.length) {
                        last_el = last_el.get(0);
                        //last_el.scrollIntoView(true);
                        last_el.parentNode.scrollTop = last_el.offsetTop;
                        $('#message_' + username).find('.message_content').scrollTop(last_el.offsetTop);
                    }
                }
            });
        }

        function save_history(username, tabs) {
            var username = username || LionFace.User.username;
            var tabs = tabs || $('.chat_div');
            var users = [];
            tabs.each( function (i,e) {
                var user = {};
                //usernames.push( $(e).attr('id').replace('name_','') );
                var username = $(e).attr('id').replace('name_','');
                user['username']=username;
                if ($(e).hasClass('new_chat_message')) {
                    user['active']=true;
                }
                else {
                    user['active']=false;
                }
                if ($(e).hasClass('tab_opened')) {
                    user['opened']=true;
                }
                else {
                    user['opened']=false;
                }
                users.push(user);
            });
            if (users) {
                socket.emit('save history', username, JSON.stringify(users)); 
            }
        }
        function load_history() {
            var url = LionFace.User.chat_loadhistory_url;
            make_request({ 
                url:url,
                multi:true,
                callback: function(data) {
                    if (data.status == 'OK') {
                        for (name in data) {
                            if (!$('#name_'+name).length) {
                                $('#names_chat_container').append(data[name].names);
                                $('#main_chat_container').append(data[name].messages);
                                socket.emit('load history', name); 
                                auto_size();
                                toggle_tabs();
                            }
                        }
                    }
                }
            });
        }


        socket.on('connect', function () {
            if (LionFace.User.is_visible) {
                $('#chat_text').html('Online');
                $('#chat_text').removeClass('offline_text').addClass('online_text');
                $('#chat_text').parents('#chat_id').find('.offline').removeClass('offline').addClass('online');
                $('.turn_off').html('Turn Off');
                socket.emit('join', LionFace.User.username, LionFace.User.name); 
                connected = true;
            }
        });

        socket.on('joined', function () {
                load_history();
        });

        socket.on('add', function (username, name) {
            // socketio bug (not me broadcast)
            if (username == LionFace.User.username) { return; }
            if ($.inArray(username, LionFace.User.friends) >= 0) {
                var user = '<li id="'+username+'"><div class="online"></div> '+name+'</li>';
                if (!$('#online_list').find('#'+username).length) {
                    $('#online_list').find('ul').append($(user).hide().fadeIn());
                    var count  = parseInt($('#online_count').html()) + 1;
                    $('#online_count').html(count);
                }
                $('#name_'+username).find('.offline').removeClass('offline').addClass('online');
            }
        });

        socket.on('remove', function (username) {
            $('#online_list').find('#'+username).fadeOut( function() { $(this).remove() });
            var count  = parseInt($('#online_count').html()) - 1;
            $('#online_count').html(count);
            if (count == 0 && $('#chat_id').data('toggled')) {
                $('#chat_id').data('toggled',false);
                $('#online_list').hide();
            }
            // remove marker
            $('#name_'+username).find('.online').removeClass('online').addClass('offline');
        });

        socket.on('chat', function (data) {
            // check if message from this user exists
            // if yes, find div, append message
            // if no, create new container
                //$('.user_content').append(data.message + "<br/>");
                console.log(data);
                if (!$('#message_'+data.username).length) {
                    //var count = $('.user_conatiner').length;
                    //var left = 255 * count + 210;
                    $('#names_chat_container').append(data.names);
                    $('#main_chat_container').append(data.messages);
                    //$('#message_'+data.username).css('left',left);
                    //blink
                    if (!$('#name_'+data.username).hasClass('new_chat_message') &&
                        !$('#message_'+data.username).find('.kind_start').length) {
                        $('#name_'+data.username).addClass('new_chat_message');
                    }
                }
                else {
                    if ($('#message_'+data.username).find('.user_content:last').length) {
                        var usernamecl = $('#message_'+data.username).find('.user_content:last').attr('class').split(' ')[1];
                    }
                    else {
                        var usernamecl = '';
                    }
                    var message = $($(data.message)[0]) 
                    var usernamefr = message.find('span').attr('class').split(' ')[1];
                    // if previous message from the same user
                    if (usernamecl == usernamefr) {
                        $('#message_'+data.username).find('.message_content').append('<div>' + message.find('.user_content').html() + '</div>');
                        $('#message_'+data.username).find('.message_content').show();
                    }
                    else {
                        $('#message_'+data.username).find('.message_content').append('<div>' + data.message + '</div>');
                        $('#message_'+data.username).find('.message_content').show();
                    }
                    if (!$('#name_'+data.username).hasClass('new_chat_message') && !$('#name_'+data.username).data('toggled')) {
                        $('#name_'+data.username).addClass('new_chat_message');
                    }
                }
                save_history();
                // if opened
                if ($('#name_'+data.username).data('toggled')) {
                    // scroll
                    var last_el = $('#message_' + data.username).find('div:last')
                    if (last_el.length) {
                        last_el = last_el.get(0);
                        //last_el.scrollIntoView(true);
                        $('#message_' + data.username).find('.message_content').scrollTop(last_el.offsetTop);
                    }
                }
        });

        $(document).on('keypress','#chat_input', function(event) {
            if (!connected) { return; }
            var $this = $(this);
            var username = $this.parents('.user_conatiner').find('.chat_username').val();
            var from = LionFace.User.username;
            var usernamecl = '';
            if (event.keyCode == 13 && $this.val()) {
                var context = {user_link : LionFace.User.url, user_name: LionFace.User.name, user_username: LionFace.User.username, message: $this.val()}
                var message = template(context); 
                // if not first message
                if ($this.parents('.user_conatiner').find('.user_content').length) {
                    //message = '<br/>' + message;
                    usernamecl = $('#message_'+username).find('.user_content:last').attr('class').split(' ')[1];
                }
                // if previous from same user
                if (usernamecl == 'message_from_'+LionFace.User.username) {
                    var context2 = {user_username: LionFace.User.username, message: $this.val()}
                    var halfmessage = template2(context2);
                    $this.parents('.user_conatiner').find('.message_content').append(halfmessage);
                }
                else {
                    $this.parents('.user_conatiner').find('.message_content').append(message);
                }

                $this.parents('.user_conatiner').find('.message_content').show();
                if (!$this.hasClass('kind_start')) {
                    socket.emit('user reply', username, from, $this.val());
                }
                else {
                    socket.emit('user message', username, from, $this.val());
                    $this.removeClass('kind_start').addClass('kind_reply');
                }
                // scroll
                var last_el = $('#message_' + username).find('div:last')
                if (last_el.length) {
                    last_el = last_el.get(0);
                    //last_el.scrollIntoView(true);
                    $('#message_' + username).find('.message_content').scrollTop(last_el.offsetTop);
                }
                $this.val('');
                return false;
            }
        });

        // chat window
        $(document).on('click', '#chat_id', function(e) {
            var $this = $(this);
            var count = parseInt($this.find('#online_count').html());
            if (count <= 0) { return; }
            var toggled = $this.data('toggled');
            if (!toggled) {
                $('#online_list').show();
                $this.data('toggled',true);
            }
            else {
                $('#online_list').hide();
                $this.data('toggled',false);
            }
        });

        // collapse conversations
        $(document).on('click', '.chat_div', function(e) {
            var $this = $(this);
            var _this = this;
            var username = $(this).attr('id').split('_')[1];
            var toggled = $this.data('toggled');
            if (!toggled) {
                $this.width(cont_width);
                var mes_order = $('#message_' + username).index('.user_conatiner');
                var $others = $('.user_conatiner:gt('+mes_order+')');
                //var left = $('#message_' + username).css('left');
                // left = parseInt(left) - ( count * 50 )
                $others.css('left',"+=50");
                $this.addClass('tab_opened');
                $this.data('toggled',true);
                $this.removeClass('new_chat_message');
                var order = $this.index()-1;
                var count_c = $('.chat_div:lt('+order+')').length;
                var opncnt = $this.index('.tab_opened');
                var opened_count = $('.tab_opened:lt('+opncnt+')').length;
                var count_o = count_c - opened_count;
                var left = (cont_width - 50 + 16 + 5) * count_o + (cont_width + 16 + 5) * opened_count + 210;
                $('#message_' + username).css('left',left);
                $('#message_' + username).show();
                // scroll
                var last_el = $('#message_' + username).find('div:last')
                if (last_el.length) {
                    last_el = last_el.get(0);
                    //last_el.scrollIntoView(true);
                    //parentNode.scrollTop
                    $('#message_' + username).find('.message_content').scrollTop(last_el.offsetTop);
                }
            }
            else {
                $this.width(cont_width-50);
                var mes_order = $('#message_' + username).index('.user_conatiner');
                var $others = $('.user_conatiner:gt('+mes_order+')');
                $others.css('left',"-=50");
                $('#message_' + username).hide();
                $this.removeClass('tab_opened');
                $this.data('toggled',false);
            }
            save_history();
        });

        $(document).on('click', '.turn_off', function(e) {
            e.stopPropagation();
            var $this = $(this);
            var text = $('#chat_text');
            var data = {};
            if (text.hasClass('offline_text')) {
                data['status'] = 'online';
            }
            else {
                data['status'] = 'offline';
            }
            make_request({
                url: LionFace.User.chat_status_url,
                data: data,
                callback: function(data) {
                    if (data.status == 'OK') {
                        if (text.hasClass('offline_text')) {
                            text.html('Online');
                            text.parents('#chat_id').find('.offline').removeClass('offline').addClass('online');
                            text.removeClass('offline_text').addClass('online_text');
                            $('.turn_off').html('Turn Off');
                            socket.emit('join', LionFace.User.username, LionFace.User.name); 
                        }
                        else {
                            text.html('Offline');
                            text.parents('#chat_id').find('.online').removeClass('online').addClass('offline');
                            text.removeClass('online_text').addClass('offline_text');
                            $('.turn_off').html('Turn On');
                            socket.emit('unjoin', LionFace.User.username); 
                        }
                    }
                }
            });
        });

        // start new conversation
        $(document).on('click', '.chat_container li', function(e) {
            if (!connected) { return; }
            var username = $(this).attr('id');
            if ($('#name_'+username).length) {
            }
            else {
                socket.emit('start chat', username, LionFace.User.username);
            }
        });

        $(document).on('click', '.remove_chat_window', function(e) {
            e.stopPropagation();
            if (!connected) { return; }
            var div = $(this).parents('.chat_div');
            var username = $(this).attr('id');
            var indx = $('#message_' + username).index('.user_conatiner');
            $('.user_conatiner:gt('+indx+')').css( 'left', function(index, style) {
                var value = parseInt(get_int(style));
                return value - 255;
            });             
            div.fadeOut( function() { $(this).remove(); save_history(); }); 
            $('#message_' + username).remove();
            socket.emit('close chat', username, LionFace.User.username);
        });

    },
};

$(document).ready(function() {        
    LionFace.Chat = new LionFace.Chat();
});
