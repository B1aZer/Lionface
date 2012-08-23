

function load_post(post, type) { 
    url = "/posts/show/";
    //var $elem = $(document.createElement('div'));
    //$(".right_col").append($elem);
    var $elem = $('.right_content');
    $elem.addClass("large_loader"); 

    $.ajax(

    {
      type: 'POST',
      url: url,
      data: {
          post_id : post,
          post_type : type
      },
      success: function(data) {
        //alert(data.html);
        $elem.removeClass("large_loader");
        $elem.html(data.html);

      },
      error: function() {
        alert('Unable to delete data.');
      }
    });    

}     

$(document).ready(function(){
    $(".profile_post").click(function() {
        var meta = $(this).metadata();
        if (meta.id != undefined) {
            load_post(meta.id, meta.type)
            }
    });
}); 
