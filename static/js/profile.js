$(function() {
  $("#postbox .postcontent").focus(function() {
    $("#postbox .postoptions").slideDown();
    if($(this).val() == 'Share something...') {
      $(this).val("");
    }
  });
  $("#postbox .postcontent").focusout(function() {
    $("#postbox .postoptions").slideUp();
    if($(this).val() == '') {
      $(this).val("Share something...");
    }
  });
  $("#postboxbutton").click(function() {
    $.ajax({
      url: '/posts/save/',
      data: $('#postform').serialize(),
      type: 'POST',
      dataType: 'json',
      success: function(data) {
        $("#postbox .postcontent").val("");
        //alert("Saved");
      },
      error: function() {
        alert("Failed to save new post.  Please try again later.");
      }
    });
    
    return false;
  })
});
