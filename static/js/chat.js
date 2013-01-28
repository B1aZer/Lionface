LionFace.Chat = function(options) {
    this.options = $.extend({
        
    }, options || {});;
    this.init();
};


LionFace.Chat.prototype = {

    init : function() {
        var me = this;
        me.bind_functions();
        me.bind_chat();
    },

    bind_chat : function() {

        var socket = io.connect("/chat");

        socket.on('connect', function () {
            $('#chat_text').html('Online');
            socket.emit('join', LionFace.User.username); 
        });

        socket.on('chat', function (data) {
                $('.user_content').append(data.message + "<br/>");
        });

        $('#chat_input').keypress(function(event) {
            var $this = $(this);
            var username = $this.parents('.user_conatiner').find('.chat_username').val();
            if (event.keyCode == 13) {
                //alert($this.val());
                socket.emit('user message', username, $this.val());
                $this.val('');
            }
        });
    },

    // Binding
    bind_functions : function() {

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
            var toggled = $this.data('toggled');
            if (!toggled) {
                $('.user_conatiner').show();
                $this.data('toggled',true);
            }
            else {
                $('.user_conatiner').hide();
                $this.data('toggled',false);
            }
        });

    },
};

$(function() {         
    LionFace.Chat = new LionFace.Chat();
});
