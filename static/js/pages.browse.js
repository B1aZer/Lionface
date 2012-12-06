LionFace.PagesBrowse = function() {
    this.init();
}


LionFace.PagesBrowse.prototype = {

    init : function() {
        var self = this;
        self.bind_functions();
        self.load_pages();
        var shifted = false;
    },

    //Binding
    bind_functions : function() {
        var self = this;
        $(document).bind('keyup keydown', function(e){self.shifted = e.shiftKey} );
        $(document).on('click','.filter',function() {
            $(this).toggleClass('filterON');
            console.log(self.shifted);
            if (self.shifted) {
                $('.filterON').removeClass('filterON');
                $(this).toggleClass('filterON');
            }
            if ($('.filterON').length) {
                $('.no_posts').hide();
                $('#page_browser').show();
                self.load_pages();
            }
            else {
                $('.no_posts').show();
                $('#page_browser').hide();
            }
        });
    },

    load_pages : function() {
        var url = "";
        var filters = new Array();
        $('.filterON').each(function () {
            filters.push(get_int($(this).attr('id')));
        }); 
        var for_send = {'filters':filters};
        make_request({
            url:url,
            type:'GET',
            data:for_send,
            callback:function(data) {
                if (data.status == 'OK') {
                    $('#page_browser').html(data.html);
                }
            }
        });

    }
}

$(function() {         
    LionFace.PagesBrowse = new LionFace.PagesBrowse()
});

