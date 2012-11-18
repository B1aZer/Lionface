LionFace.Pages = function(options) {
    this.options = $.extend({
        
    }, options || {});;
    this.init();
};


LionFace.Pages.prototype = {

    init : function() {
        var self = this;
        self.bind_functions();
    },

    // Binding
    bind_functions : function() {

        // bind event on click
        $(document).on('click','.someclass',function() {
            // create element
            var loader = $('<div>', { 'class':'large_loader'});

            // ajax request
            var url='';
            make_request({
                url:url,
                //data:{ 'some_value': some_value,
                callback: function (data) {
                },
                /*errorback: function () { 
                }
                */
            }); 
        })
    },
};

$(function() {         
    LionFace.Pages = new LionFace.Pages();
});
