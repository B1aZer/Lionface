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

        socket.on('connect', function () {
            if (LionFace.User.is_visible) {
                $('#chat_text').html('Online');
                $('#chat_text').removeClass('offline_text').addClass('online_text');
                $('#chat_text').parents('#chat_id').find('.offline').removeClass('offline').addClass('online');
                socket.emit('join', LionFace.User.username); 
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
                    $('#message_'+data.username).find('.user_content').append('<br/>' + data.message);
                }
        });

        $(document).on('keypress','#chat_input', function(event) {
            var $this = $(this);
            var username = $this.parents('.user_conatiner').find('.chat_username').val();
            var from = LionFace.User.username;
            if (event.keyCode == 13) {
                //alert($this.val());
                if (!$this.hasClass('kind_start')) {
                    socket.emit('user reply', username, from, $this.val());
                    $this.parents('.user_conatiner').find('.user_content').append('<br/>' + $this.val());
                    $this.val('');
                }
                else {
                    socket.emit('user message', username, from, $this.val());
                    $this.parents('.user_conatiner').find('.user_content').append('<br/>' + $this.val());
                    $this.removeClass('kind_start').addClass('kind_reply');
                    $this.val('');
                }
            }
        });

        // chat window
        $(document).on('click', '#chat_id', function(e) {
            var $this = $(this);
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
                            socket.emit('join', LionFace.User.username); 
                        }
                        else {
                            text.html('Offline');
                            text.parents('#chat_id').find('.online').removeClass('online').addClass('offline');
                            text.removeClass('online_text').addClass('offline_text');
                            socket.emit('unjoin', LionFace.User.username); 
                        }
                    }
                }
            });
        });

        // start new conversation
        $(document).on('click', '.chat_container li', function(e) {
            //TODO: check if connected
            var username = $(this).attr('id');
            if ($('#name_'+username).length) {
            }
            else {
                socket.emit('start chat', username, LionFace.User.username);
            }
        });

        $(document).on('click', '.remove_chat_window', function(e) {
            e.stopPropagation();
            var div = $(this).parents('.chat_div');
            var username = $(this).attr('id');
            div.fadeOut( function() { $(this).remove(); }); 
            $('#message_' + username).remove();
            $('.user_conatiner').css( 'left', function(index, style) {
                var value = parseInt(get_int(style));
                console.log(value);
                return value - 205;
            });             
            socket.emit('close chat', username, LionFace.User.username);
        });

    },
};

$(function() {         
    LionFace.Chat = new LionFace.Chat();
});
