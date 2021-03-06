function loadNewsFeed(elem, page, url) {

    var $elem = elem;
    var $data = elem.metadata();
    $elem.html("<div class='large_loader'></div>");

    if (typeof page === "undefined") {
        page = 1;
    }

    if (!url) {
        url = "/posts/feed/?page="+page;
        if($data.type == "profile")
            url = "/posts/feed/" + $data.user + "/?page="+page;
    }

    make_request({
        url:url,
        multi:true,
        callback: function(data) {
            if (page > 1) {
                $elem.replaceWith(data.html);
            }
            else {
                $elem.html(data.html);
            }
            $(document).data('ajax_finished','true');
            /** scroll to hash, not used */
            /*
            var hash = document.location.hash;
            if (hash) {
                var ids = hash.replace("#","");
                var offs = $('html, body').find('#post_'+ids).offset();
                $('html, body').animate({scrollTop:offs.top}, 500);
            }
            */
            make_excerpts();
            toggle_comments();
            if (data.page) {
                $(document).data('feed_page', data.page);
            }

            //LionFace.PostImages.bind_settings();
        },
        errorback: function() {
            console.log('Unable to retrieve data.');
        }
    });
}

function del_post_single(elem) {
    var data = $('.post_'+elem).metadata();

    if(data.type !== undefined) {

    url = "/posts/del/" + elem + "/?type="+data.type+"&ajax=true";

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

function hide_add_link() {
  if ($('.tagged').length >= 7) {
        $('.tags').hide();
        }
  else {
   $('.tags').show();
   }

}

function toggle_comments() {
    $('.toggle_comments').each( function(i,e) {
            //$(e).parents('.toggle_comments').click();
            $(e).parents('.result').find('.comments').show();
            $(e).data('toggled',true);
    });
}

function check_for_new_posts(filter, initial) {
    var filter = filter || false;
    var initial = initial || false;
    // if its not news feed
    if (!LionFace.User.feed_comet_url) {
        return;
    }
    var url = LionFace.User.feed_comet_url;
    var now = new Date(); 
    var data = {'date':now.toISOString()}
    if (filter) {
        data['filter'] = filter;
    }
    if (initial) {
        data['initial'] = initial;
    }
    make_request({
        url:url,
        type:'GET',
        data:data,
        multi:true,
        callback: function(data) {
            if (data.count) {
                if (filter == 'F') {
                    $('#friends_count').html(data.count);
                }
                if (filter == 'W') {
                    $('#following_count').html(data.count);
                }
                if (filter == 'B') {
                    $('#businesses_count').html(data.count);
                }
                if (filter == 'N') {
                    $('#nonprofits_count').html(data.count);
                }

            }
        }
    });
}



$(document).ready(function(){

    loadNewsFeed($("#news_feed"));

    hide_add_link();

    check_for_new_posts('', true);

    //checking for new posts
    if (!LionFace.User.is_anonymous) {
        setTimeout(function() {
            setInterval(function() {
                check_for_new_posts('F');
            }, 60000);
        }, 5000);
        setTimeout(function() {
            setInterval(function() {
                check_for_new_posts('W');
            }, 60000);

        }, 10000);
        setTimeout(function() {
            setInterval(function() {
                check_for_new_posts('B');
            }, 60000);

        }, 15000);
        setTimeout(function() {
            setInterval(function() {
                check_for_new_posts('N');
            }, 60000);

        }, 20000);
    }

    var shifted = false;

    $(document).bind('keyup keydown', function(e){shifted = e.shiftKey} );

    $('.tagged').hover(function () {

        $(this).find('.remove_tag').show();
        },function () {
        $(this).find('.remove_tag').hide();
    });

    $('.feed_type').live('click',function () {
        var self = $(this);
        var tag_val = $(this).attr('id');
        var send = 'filter_name='+tag_val;


        if (shifted) {
            if (self.hasClass('filterON')) {
                if ($('.filterON').length == 1) {
                    self.removeClass('filterON').addClass('filter'); 
                    send = send + '&single=1';
                }
            }
        }
        else {
            $('.filterON').removeClass('filterON').addClass('filter'); 
            send = send + '&single=1';
        }


        if ($(this).hasClass('filterON')) {
            url = '/account/filter/remove/';
            make_request({
                url: url,
                data: send,
                callback: function(html) {
                    if (html.status == 'OK') {

                        self.removeClass('filterON');
                        self.addClass('filter');
                        self.attr('title','Turn filter on.');
                        loadNewsFeed($("#news_feed"));
                    }
                },
                errorback: function (XMLHttpRequest, textStatus, errorThrown) {
                    alert('Sorry! impossible to deactivate filter');
                }

            });

        }
        else {
            url = '/account/filter/add/';
            make_request({
                    url: url,
                    multu: true,
                    data: send,
                    callback: function(html) {
                        if (html.status == 'OK') {

                            self.removeClass('filter');
                            self.addClass('filterON');
                            self.attr('title','Turn filter off.');
                            if (tag_val == 'Friends') {
                                $('#friends_count').html('');
                            }
                            if (tag_val == 'Following') {
                                $('#following_count').html('');
                            }
                            if (tag_val == 'Businesses') {
                                $('#businesses_count').html('');
                            }
                            if (tag_val == 'Nonprofits') {
                                $('#nonprofits_count').html('');
                            }
                            $('.active_trending').removeClass('active_trending');
                            loadNewsFeed($("#news_feed"));
                        }
                    },
                    errorback: function (XMLHttpRequest, textStatus, errorThrown) {
                        alert('Sorry! impossible to deactivate filter');
                    }

            });

        }
      });

  $('.tagged').live('click',function () {
        var self = $(this)
        var tag_val = $(this).contents()[0];
        var send = 'tag_name='+tag_val.textContent;
        // single filter
        if (shifted) {
            //single filter
            if (self.hasClass('filterON')) {
                if ($('.filterON').length == 1) {
                    self.removeClass('filterON').addClass('filter'); 
                    send = send + '&single=1';
                }
            }
        }
        else {
            $('.filterON').removeClass('filterON').addClass('filter'); 
            send = send + '&single=1';
        }
        if ($(this).hasClass('filterON')) {
                url = '/tags/deact/';

                  make_request({
                    url: url,
                    multi: true,
                    data: send,
                    callback: function(html) {
                        self.removeClass('filterON');
                        self.addClass('filter');
                        self.attr('title','Turn filter on.');
                        loadNewsFeed($("#news_feed"));
                    },
                    errorback: function (XMLHttpRequest, textStatus, errorThrown) {
                        console.log('Sorry! impossible to deactivate tag');
                    }

                  });
        }
        else {
             url = '/tags/act/';

                  make_request({
                    url: url,
                    multi: true,
                    data: send,
                    callback: function(html) {
                        self.removeClass('filter');
                        self.addClass('filterON');
                        self.attr('title','Turn filter off.');
                        $('.active_trending').removeClass('active_trending');
                        loadNewsFeed($("#news_feed"));
                    },
                    errorback: function (XMLHttpRequest, textStatus, errorThrown) {
                        console.log('Sorry! impossible to activate tag');
                    }

                  });
        }
    });

  $('.add_tag').live('click',function (e) {
      e.preventDefault();
      e.stopPropagation();

      var self = $(this);

      var link = $(this).parent();
      var link_add = link.clone();
      var last_link = link

      var form = $('<form id="foma" />');
      form.html('<input type="text" id="editbox" name="tags"><input id="button_save" type="submit" name="submit" class="blue_btn" value="Follow">')
      $('.tags').html(form);
      $('#editbox').focus();

      form.submit(function(e) {
        e.preventDefault();
        url = '/tags/add/';

              make_request({
                url: url,
                multi: true,
                data: $(this).serialize(),
                callback: function(html) {
                    if (html.tags && html.tags.length < 2)
                    {
                        link.html(html.tags).addClass('tagged');
                        link.append('<span class="remove_tag" style="float:right; display:none">x</span>');
                        link.hover(function () {
                            $(this).find('.remove_tag').show();
                            },function () {
                            $(this).find('.remove_tag').hide();
                        });
                        link.removeClass('tags');
                        link.removeClass('filter');
                        link.addClass('filterON');
                        link.attr('title','Turn filter off.');
                        link.attr('style','');
                        link.after(link_add);
                        hide_add_link();
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
                            link_tag.removeClass('filter');
                            link_tag.addClass('filterON');
                            link_tag.attr('title','Turn filter off.');
                            link_tag.attr('style','');
                            last_link.after(link_tag)
                            last_link = link_tag

                        }
                        link.remove();
                        last_link.after(link_add);
                        hide_add_link();
                    }
                    else
                    {
                        link.html(link_add.html())
                    }
                    if (html.tags) {
                        loadNewsFeed($("#news_feed"));
                        }
                },
                errorback: function (XMLHttpRequest, textStatus, errorThrown) {
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

       var link = $(this).parent()
       var tag_val = $(this).parent().contents()[0];
       var send = 'tag_name='+tag_val.textContent;

        make_request({
            url: url,
            multi:true,
            data: send,
            callback: function(html) {
                if (html.status == 'OK' )
                    {
                    link.fadeOut();
                    link.remove();
                    hide_add_link();
                    }
                    loadNewsFeed($("#news_feed"));
                },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                console.log('Impossible to delete tag');
            }

        });
    });

    /** Load more post in newsfeed */
    $(document).on('click','#see_more_feed',function(e){
        e.preventDefault();
        var self = $(this)
        var page = get_int(self.attr('href'));
        if ($("#news_feed").length) {
            $("#news_feed").append("<div id='new_posts'></div>");
            $("#new_posts").addClass($("#news_feed").attr('class'));
        }
        self.remove();
        loadNewsFeed($("#new_posts"),page);
    })

    $(document).on('click','#see_tags_feed',function(e){
        e.preventDefault();
        var self = $(this);
        var url = self.attr('href');
        console.log(url);
        if ($("#news_feed").length) {
            $("#news_feed").append("<div id='new_posts'></div>");
            $("#new_posts").addClass($("#news_feed").attr('class'));
        }
        self.remove();
        loadNewsFeed($("#new_posts"),undefined,url);
    })

    $(document).on('click', '.tringing-tags', function(e) {
        e.preventDefault();
        var $this = $(this);
        $('.active_trending').removeClass('active_trending');
        var url = $(this).find('.tag_link').attr('href');
        $("#news_feed").html("<div class='large_loader'></div>");
        make_request({
            url:url,
            callback: function(data) {
                if (data.status == 'OK') {
                    $('.filterON').toggleClass('filterON').toggleClass('filter');
                    $("#news_feed").html(data.html);
                    $this.addClass('active_trending');
                }
            },
            errorback: function(data) {
                    $("#news_feed").html('Unable to retrieve data.');
            }
        });
    });

    // select friends if none selected
    if (!$('.filterON').length) {
        $('#Friends').removeClass('filter').addClass('filterON');
    }

});

