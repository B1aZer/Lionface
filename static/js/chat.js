LionFace.Chat = function(options) {
    this.options = $.extend({
        
    }, options || {});;
    this.init();
};


LionFace.Chat.prototype = {

    init : function() {
        var me = this;
        me.bind_functions();
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
