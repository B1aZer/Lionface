$(document).ready(function() {

    $(document).on('click', '.related', function(){
        var name = $(this).html();
        var url = '';
        if (name == "Friend") {
            url='?friends';
            }
        if (name == "Following") {
            url='?following';
            }
        if (name == "Followers") {
            url='?followers';
            }
        make_request({
            url:url, 
            callback:function (data) {
                if (data.html) {
                    $('#related_users').html(data.html);
                }
            }
        });

    }); 

})
