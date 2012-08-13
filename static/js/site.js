function hookLinks() {
  // Friend links.
  $('.link-add-friend').unbind('click');
  $('.link-add-friend').click(function() {
    var data = $(this).metadata();
    var $this = $(this);
    if(data.user !== undefined) {
      $this.unbind('click');
      var $ohtml = $this.html();
      $this.append('<div class="link_loader"></div>');
      
      $.ajax('/account/friend/add/',{
        type: 'GET',
        data: 'user=' + encodeURIComponent(data.user),
        success: function(data) {
          $this.html($ohtml);
          if(data.status == 'OK') {
            $this.html('Friend request sent.');
          }
        },
        error: function() {
          hookLinks();
          $this.html($ohtml);
        }
      });
    }
    return false;
  });
  
  $('.link-accept-friend').unbind('click');
  $('.link-accept-friend').click(function() {
    var data = $(this).metadata();
    var $this = $(this);
    if(data.request !== undefined) {
      $this.unbind('click');
      var $outElem = $this.closest('.link-output');
      var $ohtml = $outElem.html();
      $outElem.html('<div class="link_loader"></div>');
      $.ajax('/account/friend/accept/' + data.request + '/',{
        type: 'GET',
        success: function(data) {
          $outElem.html($ohtml);
          if(data.status == 'OK') {
            $outElem.html('Friend request accepted.');
          }
        },
        error: function() {
          $outElem.html($ohtml);
          hookLinks();
        }
      });
    }
    return false;
  });

  $('.link-decline-friend').unbind('click');
  $('.link-decline-friend').click(function() {
    var data = $(this).metadata();
    var $this = $(this);
    if(data.request !== undefined) {
      $this.unbind('click');
      var $outElem = $this.closest('.link-output');
      var $ohtml = $outElem.html();
      $outElem.html('<div class="link_loader"></div>');
      $.ajax('/account/friend/decline/' + data.request + '/',{
        type: 'GET',
        success: function(data) {
          $outElem.html($ohtml);
          if(data.status == 'OK') {
            $outElem.html('Friend request declined.');
          }
        },
        error: function() {
          $outElem.html($ohtml);
          hookLinks();
        }
      });
    }
    return false;
  });
}

$(function() {
  hookLinks();
});