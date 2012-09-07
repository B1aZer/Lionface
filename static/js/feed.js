function loadNewsFeed(elem) {
  var $elem = elem;
  var $data = elem.metadata();
  $elem.html("<div class='large_loader'></div>");
  
  url = "/posts/feed/";
  if($data.type == "profile")
    url = "/posts/feed/" + $data.user + "/";

  if (window.location.pathname.indexOf('lionface') >= 0) 
  { 
    url = '/lionface' +  url;
  }
  
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


function del_post_single(elem) { 
    var data = $('.post_'+elem).metadata();

    if(data.type !== undefined) {

    url = "/posts/del/" + elem + "?type="+data.type;

  if (window.location.pathname.indexOf('lionface') >= 0) 
  { 
    url = '/lionface' +  url;
  }
    
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

function saving_tag(elem) {

}
$(document).ready(function(){
  loadNewsFeed($("#news_feed"));
  //alert(window.location.pathname);
  $('.add_tag').click(function (e) {
      e.preventDefault();
      e.stopPropagation();

      var form = $('<form id="foma" />');
      form.html('<input type="text" id="editbox" name="tags"><input id="button_save" type="submit" name="submit">')
      $('.tags').html(form);
      $('#editbox').focus(); 

      form.submit(function(e) {
        e.preventDefault();
        url = '/tags/add/';
         if (window.location.pathname.indexOf('lionface') >= 0) 
              { 
                url = '/lionface' +  url;
              }    

              $.ajax({
                type: "POST",
                data: $(this).serialize(),
                url: url,
                success: function(html, textStatus) {
                alert('added');
                },
                error: function (XMLHttpRequest, textStatus, errorThrown) {
                alert('wrong');
                }

            });     


        });

  });
    $(document).click(function() {
        /*$('.tags').html('<span class="add_tag">Add +</span>');*/
    });
  


});

