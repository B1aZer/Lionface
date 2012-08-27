$(function() {
    $('.noPhoto').hover(
            function(){$('.upload').slideDown(500);},
            function(){$('.upload').slideUp(500);});

    $("#postbox .postcontent").focus(function() {
        //$("#postbox .postoptions").slideDown();
        if($(this).val() == 'Share something...') {
            $(this).val("");
        }
    });
    $("#postbox .postcontent").focusout(function() {
        //$("#postbox .postoptions").slideUp();
        if($(this).val() == '') {
            $(this).val("Share something...");
        }
    });

    var url = '/posts/save/'

     if (window.location.pathname.indexOf('lionface') >= 0) 
  { 
    url = '/lionface' +  url;
  }       
    
    $("#postboxbutton").click(function() {
        $.ajax({
            url: url,
            data: $('#postform').serialize(),
            type: 'POST',
            dataType: 'json',
            success: function(data) {
                //$("#postbox .postcontent").val("");
                $("#news_feed").prepend(data.html);
            },
            error: function() {
                alert("Failed to save new post.  Please try again later.");
            }
        });

        return false;
    })
    $('.postcontent').keypress(function(e){
        if(e.which == 13){
            $.ajax({
                url: url,
                data: $('#postform').serialize(),
                type: 'POST',
                dataType: 'json',
                success: function(data) {
                    //$("#postbox .postcontent").val("");
                    $("#news_feed").prepend(data.html);
                },
                error: function() {
                    alert("Failed to save new post.  Please try again later.");
                }
            });

            return false;   
        }
    });
});
