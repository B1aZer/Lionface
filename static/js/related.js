$(document).ready(function() {

    if (window.location.search) {
        var get_param = window.location.search.replace( "?", "" );
        $('.filter').each(function () {
            if ($(this).html() == get_param) {
                $(this).toggleClass('filter');
                $(this).toggleClass('filterON');
            }
        });
    }

    $(document).on('click', '.related', function(){
        $(this).toggleClass('filterON');
        $(this).toggleClass('filter');

        params = [];

        $('.filterON').each(function () {
            params.push("&"+$(this).html());
        });
        if (params) {
            params = "?"+params.join("").slice(1)+"&ajax";
            if (params == "?&ajax") {
                params = [];
            }
        }
        var url = params;
        if (params.length) {
            make_request({
                url:url, 
                callback:function (data) {
                    if (data.html) {
                        $('#related_users').html(data.html);
                    }
                }
            });
        }
        else {
            $('#related_users').html('<p align="center" class="no_posts">No results found.</p>');
        }

    }); 

})
