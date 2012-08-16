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


$(function() {
  loadNewsFeed($("#news_feed"));
});
