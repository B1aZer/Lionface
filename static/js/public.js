function ReverseContentDisplay(d) {
    if(d.length < 1) { return; }
    if(document.getElementById(d).style.display == "none") { document.getElementById(d).style.display = "block"; }
    else { document.getElementById(d).style.display = "none"; }
}

$(document).ready(function() {

    $(document).on('click','.public_link',function() {
        var name = $(this).attr('id');
        var url = '/micro/';
        var self = $(this);
        $.ajax(url,{
                type: 'GET',
                data: 'name=' + name,
                success: function(data) {
                    if(data.status == 'OK') {
                        $('.enabled_results').html(data.html);
                        $('.enabled_results').show();
                        $('.container_active').removeClass('container_active');
                        self.addClass('container_active');
                    }
                },
                error: function() {
                    console.log('error at public retrieval');
                }
            });  
    });  

})
