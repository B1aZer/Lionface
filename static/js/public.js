function ReverseContentDisplay(d) {
    if(d.length < 1) { return; }
    if(document.getElementById(d).style.display == "none") { document.getElementById(d).style.display = "block"; }
    else { document.getElementById(d).style.display = "none"; }
}

$(document).ready(function() {

    $(document).on('click','.public_link',function() {
        var name = $(this).attr('id');
        var url = '/micro/';
        $.ajax(url,{
                type: 'GET',
                data: 'name=' + name,
                success: function(data) {
                    if(data.status == 'OK') {
                        $('.enabled_results').html(data.html);
                        $('.enabled_results').show();
                    }
                },
                error: function() {
                    console.log('error at public retrieval');
                }
            });  
    });  

})
