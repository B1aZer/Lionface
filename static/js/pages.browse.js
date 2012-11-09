LionFace.PagesBrowse = function() {
    this.init();
}


LionFace.PagesBrowse.prototype = {

    init : function() {
        var self = this;
        self.bind_functions();
        self.load_pages();
    },

    //Binding
    bind_functions : function() {
        var self = this;
        $(document).on('click','.filter',function() {
            $(this).toggleClass('filterON');
            self.load_pages();
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

