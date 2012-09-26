$(function() {

    //restrict image size and format before upload
    $('#id_photo').bind('change', function() {
            console.log(this.files[0].type);
            console.log(this.files[0].size);
            if(this.files[0].size > 1000141) {
                $('#submit_img_btn').hide();
                if ($('.errorlist').length) {
                    $('.errorlist').html('<li>Image file too large ( &gt; 1mb )</li>');
                }
                else {
                    $('.upload_form').prepend('<ul class="errorlist"><li>Image file too large ( &gt; 1mb )</li></ul>');
                }
            } 
            else if(this.files[0].type == 'image/gif') {
                $('#submit_img_btn').hide();
                if ($('.errorlist').length) {
                    $('.errorlist').html('<li>Gif images are not allowed</li>');
                }
                else {
                    $('.upload_form').prepend('<ul class="errorlist"><li>Gif images are not allowed</li></ul>');
                }      
            }
            else if(this.files[0].type.indexOf("image") == -1) {
                $('#submit_img_btn').hide();
                if ($('.errorlist').length) {
                    $('.errorlist').html('<li>Please upload a valid image</li>');
                }
                else {
                    $('.upload_form').prepend('<ul class="errorlist"><li>Please upload a valid image</li></ul>');
                }      
            }       
            else{
                $('#submit_img_btn').show();
                $('.errorlist').html(''); 
            }
        });

    $("#upload_picture").click(function(event){
      event.stopPropagation();
      $('.upload_form').show(); 
    });  

    $("#reset_picture").click(function(event){
      event.stopPropagation();
    });

    $("#send_message").click(function(event){
      event.stopPropagation();
      $('.send_message_form').show(); 
    });

    $('.noPhoto').hover(
            function(){$('.upload').show();},
            function(){$('.upload').hide();});

    $("#postbox .postcontent").focus(function() {
        //$("#postbox .postoptions").slideDown();
        if($(this).val() == 'Share something...') {
            $(this).val("");
        }
    });
    $("#postbox .postcontent").focusout(function() {
        //$("#postbox .postoptions").slideUp();
        if($(this).val() == '') {
            $(this).val("Share something...");
        }
    });


    $("#postboxbutton").click(function() {
        var url = '/posts/save/'
        make_request({
            url:url,
            data: $('#postform').serialize(), 
            callback: function(data) {
                    $("#news_feed").prepend(data.html);
                    $('.postbox_textarea').val('');
            },
        });
        return false;
    });

/*
//Submit on enter

    $('.postcontent').keypress(function(e){
        if(e.which == 13){
            $.ajax({
                url: url,
                data: $('#postform').serialize(),
                type: 'POST',
                dataType: 'json',
                success: function(data) {
                    //$("#postbox .postcontent").val("");
                    $("#news_feed").prepend(data.html);
                    $('.postbox_textarea').val('');
                },
                error: function() {
                    alert("Failed to save new post.  Please try again later.");
                }
            });

            return false;   
        }
    });
*/
    

    $('.postbox_textarea').autosize();

});
