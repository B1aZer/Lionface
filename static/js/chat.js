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

        socket.on('connect', function () {
            if (LionFace.User.is_visible) {
                $('#chat_text').html('Online');
                $('#chat_text').removeClass('offline_text').addClass('online_text');
                $('#chat_text').parents('#chat_id').find('.offline').removeClass('offline').addClass('online');
                $('.turn_off').html('Turn Off');
                socket.emit('join', LionFace.User.username); 
                connected = true;
            }
        });

        socket.on('chat', function (data) {
            // check if message from this user exists
            // if yes, find div, append message
            // if no, create new container
                //$('.user_content').append(data.message + "<br/>");
                console.log(data);
                if (!$('#message_'+data.username).length) {
                    var count = $('.user_conatiner').length + 1;
                    var left = 205 * count + 5;
                    $('#names_chat_container').append(data.names);
                    $('#main_chat_container').append(data.messages);
                    $('#message_'+data.username).css('left',left);
                }
                else {
                    var usernamecl = $('#message_'+data.username).find('.user_content:last').attr('class').split(' ')[1];
                    var message = $($(data.message)[2]) 
                    var usernamefr = message.attr('class').split(' ')[1];
                    // if previous message from the same user
                    if (usernamecl == usernamefr) {
                        $('#message_'+data.username).find('.message_content').append('<br/>' + message.html());
                        $('#message_'+data.username).find('.message_content').show();
                    }
                    else {
                        $('#message_'+data.username).find('.message_content').append('<br/>' + data.message);
                        $('#message_'+data.username).find('.message_content').show();
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
                var message = '<a href="'+LionFace.User.url+'">'+LionFace.User.name+'</a>: <span class="user_content message_from_'+LionFace.User.username+'">'+$this.val()+'</span>' 
                // if not first message
                if ($this.parents('.user_conatiner').find('.user_content').length) {
                    message = '<br/>' + message;
                    usernamecl = $('#message_'+username).find('.user_content:last').attr('class').split(' ')[1];
                }
                // if previous from same user
                if (usernamecl == 'message_from_'+LionFace.User.username) {
                    var halfmessage = '<br/>' + '<span class="user_content message_from_'+LionFace.User.username+'">'+$this.val()+'</span>';
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
            if (!connected) { return; }
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
                            socket.emit('join', LionFace.User.username); 
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
            div.fadeOut( function() { $(this).remove(); }); 
            $('#message_' + username).remove();
            $('.user_conatiner').css( 'left', function(index, style) {
                var value = parseInt(get_int(style));
                return value - 205;
            });             
            socket.emit('close chat', username, LionFace.User.username);
        });

    },
};

$(function() {         
    LionFace.Chat = new LionFace.Chat();
});
