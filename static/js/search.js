LionFace.Search = function() {
    this.init();
}


LionFace.Search.prototype = {

    init : function() {
        var self = this;
        self.bind_functions();
    },

    //Binding
    bind_functions : function() {

        //search filters
        $(document).on('click','.seacrh_feed',function(e) {
            var url = '/search_ajax/'
            var loader = $('<div>', { 'class':'large_loader'});
            var self = $(this)
            var search_str = window.location.search;
            e.preventDefault();
            //one at a time
            $('.filterON').toggleClass('filterON');
            self.toggleClass('filterON');
            var filter_val = self.attr('id').replace('search_','');
            url = url + search_str + "&filter=" + filter_val;
            $('#search_form_result').html(loader);
            make_request({
                url:url,
                type: 'GET',
                callback: function (data) {
                    $('#search_form_result').replaceWith(data);
                    // pagination
                    if ($('#search_next').length) {
                        var next_url = $('#search_next').attr('href');

                        var re = /&page=(\d)/g;
                        var page_num = re.exec(next_url)[1];
                        
                        $('#search_next').attr('href', url + "&page=" + page_num);
                    }
                },
                errorback: function () {
                    $('#search_form_result').replaceWith('error in request');
                }
            });
        });

    },
}

$(function() {         
    LionFace.Search = new LionFace.Search()
});

