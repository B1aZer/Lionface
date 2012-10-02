

function load_post(post, type) { 
    url = "/posts/show/";

    var $elem = $('.right_content');
    $elem.html("");
    $elem.addClass("large_loader"); 

    make_request({
      url: url,
      data: {
          post_id : post,
          post_type : type
      },
      callback: function(data) {
        //alert(data.html);
        $elem.removeClass("large_loader");
        $elem.html(data.html);
        make_excerpts();

      },
      errorback: function() {
        alert('Unable to retrieve data.');
        $elem.removeClass("large_loader");
      }
    });    

}     

$(document).ready(function(){
    $(document).on('click',".profile_post, .shared_post, .comment_submitted, .follow_comment, .follow_shared", function(e) {
        var starter = document.elementFromPoint(e.clientX, e.clientY);  
        if ($(starter).is('a')) {
            return;
            }
        var meta = $(this).metadata();
        if (meta.id) {
            load_post(meta.id, meta.type)
            }
        else {
            $('.right_content').html("");
            }
    });

    $(document).on('click','.nav_link', function() { 
        url = $(this).attr('href');

        $.ajax({
                type: 'GET',
                url: url,
                success: function(data) {
                    $('.left_col').replaceWith(data);
                },
                error: function() {
                    console.log('fail');
                } 
            });

        return false;

    });           

    $(document).on('click',".notification", function(e) {
        if ($(this).find('.new_notification').length) {
            $(this).find('.new_notification').removeClass('new_notification');
        }
    });
}); 
