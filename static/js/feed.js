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

$(function() {
  loadNewsFeed($("#news_feed"));
});