function loadNewsFeed(elem, qnt) {
    var $elem = elem;
    var $data = elem.metadata();
    $elem.html("<div class='large_loader'></div>");

    url = "/posts/timeline/" + qnt;

    $.ajax(url,
        {
            success: function(data) {
                $elem.html(data);
                $(window).data('num','5')
            },
            error: function() {
                $elem.html('Unable to retrieve data.');
            }
        });
}

function appNewsFeed(qnt) {
    var $elem = $(document.createElement('div'));
    $("#news_feed").append($elem)
    $(window).data('ajaxready', false);

    $elem.html("<div class='large_loader'></div>");

    url = "/posts/timeline/" + qnt;
    
    $.ajax(url,
        {
            success: function(data) {
                $("#news_feed").append(data)
                $elem.hide();
                $(window).data('ajaxready', true);
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

    


$(window).scroll(function(){
    if ($(window).data('ajaxready') == false) return; 
    if  ($(window).scrollTop() == $(document).height() - $(window).height()){

        appNewsFeed($(window).data('num'));
        var num = parseInt($(window).data('num')) + 5; 
        $(window).data('num',num);
    }
});



$(function() {
    loadNewsFeed($("#news_feed"),10);
});

function HideContent(d) {
if(d.length < 1) { return; }
document.getElementById(d).style.display = "none";
}
function ShowContent(d) {
if(d.length < 1) { return; }
document.getElementById(d).style.display = "block";
}
function ReverseContentDisplay(d) {
if(d.length < 1) { return; }
if(document.getElementById(d).style.display == "none") { document.getElementById(d).style.display = "block"; }
else { document.getElementById(d).style.display = "none"; }
}    
