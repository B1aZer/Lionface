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

        var socket = io.connect("/chat");
        var connected = false;

        function save_history(username, tabs) {
            var username = username || LionFace.User.username;
            var tabs = tabs || $('.chat_div');
            var usernames = [];
            tabs.each( function (i,e) {
                usernames.push( $(e).attr('id').replace('name_','') );
            });
            console.log(username);
            console.log(usernames);
            if (usernames) {
                socket.emit('save history', username, JSON.stringify(usernames)); 
            }
        }
        function load_history() {
            var url = LionFace.User.chat_loadhistory_url;
            make_request({ 
                url:url,
                multi:true,
                callback: function(data) {
                    if (data.status == 'OK') {
                        console.log(data);
                        for (name in data) {
                            if (!$('#name_'+name).length) {
                                var count = $('.user_conatiner').length;
                                var left = 255 * count + 210;
                                $('#names_chat_container').append(data[name].names);
                                $('#main_chat_container').append(data[name].messages);
                                $('#message_'+name).css('left',left);
                                socket.emit('load history', name); 
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
                load_history();
            }
        });

        socket.on('add', function (username, name) {
            // socketio bug (not me broadcast)
            if (username == LionFace.User.username) { return; }
            var user = '<li id="'+username+'"><div class="online"></div> '+name+'</li>';
            if (!$('#online_list').find('#'+username).length) {
                $('#online_list').find('ul').append($(user).hide().fadeIn());
                var count  = parseInt($('#online_count').html()) + 1;
                $('#online_count').html(count);
            }
            $('#name_'+username).find('.offline').removeClass('offline').addClass('online');
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
                    var count = $('.user_conatiner').length;
                    var left = 255 * count + 210;
                    $('#names_chat_container').append(data.names);
                    $('#main_chat_container').append(data.messages);
                    $('#message_'+data.username).css('left',left);
                    //blink
                    if (!$('#name_'+data.username).hasClass('new_chat_message') &&
                        !$('#message_'+data.username).find('.kind_start').length) {
                        $('#name_'+data.username).addClass('new_chat_message');
                    }
                    save_history();
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
                        console.log('same');
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
        });

        $(document).on('keypress','#chat_input', function(event) {
            if (!connected) { return; }
            var $this = $(this);
            var username = $this.parents('.user_conatiner').find('.chat_username').val();
            var from = LionFace.User.username;
            var usernamecl = '';
            if (event.keyCode == 13) {
                var message = '<div style="background: #FAFCFE; padding: 4px 0; margin: 4px 0;"> <a href="'+LionFace.User.url+'">'+LionFace.User.name+'</a>: <span class="user_content message_from_'+LionFace.User.username+'">'+$this.val()+'</span></div>' 
                // if not first message
                if ($this.parents('.user_conatiner').find('.user_content').length) {
                    //message = '<br/>' + message;
                    usernamecl = $('#message_'+username).find('.user_content:last').attr('class').split(' ')[1];
                }
                // if previous from same user
                if (usernamecl == 'message_from_'+LionFace.User.username) {
                    var halfmessage = '<div>' + '<span class="user_content message_from_'+LionFace.User.username+'">'+$this.val()+'</span>' +'</div>';
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
                $this.val('');
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

        $(document).on('click', '.chat_div', function(e) {
            var $this = $(this);
            var username = $(this).attr('id').split('_')[1];
            var toggled = $this.data('toggled');
            if (!toggled) {
                $('#message_' + username).show();
                $this.data('toggled',true);
                $this.removeClass('new_chat_message');
            }
            else {
                $('#message_' + username).hide();
                $this.data('toggled',false);
            }
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
            div.fadeOut( function() { $(this).remove(); save_history(); }); 
            $('#message_' + username).remove();
            $('.user_conatiner').css( 'left', function(index, style) {
                var value = parseInt(get_int(style));
                return value - 255;
            });             
            socket.emit('close chat', username, LionFace.User.username);
        });

    },
};

$(document).ready(function() {        
    LionFace.Chat = new LionFace.Chat();
});
