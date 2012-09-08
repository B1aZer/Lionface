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

$(document).ready(function(){

  loadNewsFeed($("#news_feed"));

  $('.tagged').hover(function () {
    $(this).find('.remove_tag').show();
    },function () {
    $(this).find('.remove_tag').hide();
    });

  $('.add_tag').live('click',function (e) {
      e.preventDefault();
      e.stopPropagation();

      var self = $(this)

      var link = $(this).parent();
      var link_add = link.clone();
      var last_link = link

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
                console.log(html.tags);
                    if (html.tags && html.tags.length < 2)
                    { 
                        console.log(html.tags.length);
                        link.html(html.tags).addClass('tagged');
                        link.append('<span class="remove_tag" style="float:right; display:none">x</span>');
                        link.hover(function () {
                            $(this).find('.remove_tag').show();
                            },function () {
                            $(this).find('.remove_tag').hide();
                        });
                        link.removeClass('tags');
                        link.after(link_add);
                    }   
                    else if (html.tags && html.tags.length >= 2) 
                    {
                        for (var i=0; i<html.tags.length; i++) 
                        {
                            link_tag = link.clone()
                            link_tag.html(html.tags[i]).addClass('tagged');
                            link_tag.append('<span class="remove_tag" style="float:right; display:none">x</span>');
                            link_tag.hover(function () {
                                $(this).find('.remove_tag').show();
                                },function () {
                                $(this).find('.remove_tag').hide();
                            });
                            link_tag.removeClass('tags');
                            last_link.after(link_tag)
                            last_link = link_tag

                        }
                        link.hide();
                        last_link.after(link_add);
                    }
                    else 
                    {
                        link.html(link_add.html())
                    }
                },
                error: function (XMLHttpRequest, textStatus, errorThrown) {
                    alert('Sorry! impossible to save tag');
                }

            });     


        });

      $('#editbox').blur(function(e) {
          if ($(this).parent().parent().is(':hover') === false) {
              link.html('<span class="add_tag" >Add +</span>');
              }
            
      });

  });

    $('.remove_tag').live('click',function (e) {
        e.preventDefault();
        e.stopPropagation(); 

        url = '/tags/rem/';
        if (window.location.pathname.indexOf('lionface') >= 0) 
          { 
            url = '/lionface' +  url;
          }    

       var link = $(this).parent()
       var tag_val = $(this).parent().contents()[0];
       var send = 'tag_name='+tag_val.textContent;

        $.ajax({
            type: "POST",
            data: send,
            url: url,
            success: function(html, textStatus) {
            if (html.status == 'OK' )
                { 
                link.fadeOut();
                }
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                alert('Impossible to delete tag');
            }

        }); 
    }); 
  


});

