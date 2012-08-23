function loadNewsFeed(elem) {
  var $elem = elem;
  var $data = elem.metadata();
  $elem.html("<div class='large_loader'></div>");
  
  url = "/posts/feed/";
  if($data.type == "profile")
    url = "/posts/feed/" + $data.user + "/";
  
  $.ajax(url,
    {
      success: function(data) {
        $elem.html(data);
        $(window).data('ajax_finished','true');
        var hash = document.location.hash;
        if (hash) {
            var ids = hash.replace("#","");
            var offs = $('html, body').find('#post_'+ids).offset();
            $('html, body').animate({scrollTop:offs.top}, 500); 
        }

      },
      error: function() {
        $elem.html('Unable to retrieve data.');
      }
    });
}


function del_post(elem) { 
    url = "/posts/del/" + elem + "/";

    $.ajax(url,
    {
      success: function(data) {
        $('.post_'+elem).prev('hr').hide()
        $('.post_'+elem).fadeOut()
      },
      error: function() {
        alert('Unable to delete data.');
      }
    });    

}

function del_post_single(elem) { 
    var data = $('.post_'+elem).metadata();

    if(data.type !== undefined) {

    url = "/posts/del/" + elem + "?type="+data.type;
    }
    $.ajax(url,
    {
      success: function(data) {
          $('.post_'+elem).prev('hr').hide();
          $('.post_'+elem).fadeOut();
      },
      error: function() {
        alert('Unable to delete data.');
      }
    }); 

}     

$(document).ready(function(){
  loadNewsFeed($("#news_feed"));
});

              
