LionFace.Pages = function() {
    this.runner();
}


LionFace.Pages.prototype = {

    runner : function() {
        this.bind_functions();

    },

    //Binding
    bind_functions : function() {
        $(document).on('click','#business_submit',function(e) {
            e.preventDefault();
            var select = $('<select name="type" id="id_type" >' +
                    '<option value="BS" selected="selected">Business Page</option>' +
                    '<option value="NP">Nonprofit Page</option>' +
                    '</select>')
            select.hide();
            $(this).append(select);
            $('#business_submit_form').submit();
        });

        $(document).on('click','#nonprofit_submit',function(e) {
            e.preventDefault();
            var select = $('<select name="type" id="id_type" >' +
                    '<option value="BS">Business Page</option>' +
                    '<option value="NP" selected="selected">Nonprofit Page</option>' +
                    '</select>')
            select.hide();
            $(this).append(select);
            $('#nonprofit_submit_form').submit();
        });

        /** label for */
        $(document).on('click','label',function(e) {
            var checkbox = $(this).prev('input')
            if (checkbox.prop("checked")) {
                checkbox.prop('checked', false);
            }
            else {
                checkbox.prop('checked', true);
            }
        });

        /** love counts */
        $(document).on('click','.love_button',function(e) {
            e.preventDefault();
            var me = $(this);
            var url = '/pages/love_count/';
            var vote = 'up';
            var love_count = parseInt($('.love_count').html());
            if ($(this).hasClass('loved')) {
                vote = 'down';
            }
                make_request({
                    url:url,
                    data: {
                        'vote': vote,
                        'page_id': LionFace.User.page_id,
                    },
                    callback: function(data) {
                        if (data.status == 'OK') {
                            if (vote == 'up') {
                                me.html('Loved');
                                me.addClass('loved');   
                                love_count = love_count + 1;
                                
                            }
                            else {
                                me.html('Love');
                                me.removeClass('loved'); 
                                love_count = love_count - 1;
                            }
                            $('.love_count').html(love_count);
                        }
                    }
                });
        });
    },
}

$(function() {         
    LionFace.Pages = new LionFace.Pages();
});
