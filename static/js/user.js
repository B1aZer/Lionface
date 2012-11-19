//Common functions
LionFace.User.check_option = function(option) {
    var url = '/check/permissions/';
    if (!option) {
        return
    }
    make_request({
        url:url,
        type:'GET',
        data:{
            'option':option,
        },
        callback: function(data) {
            if (data.status == 'OK') {
                LionFace.User.options[option]=data.value;
            }
        }
    });
}

//from pages.js
LionFace.User.Pages_sortable_friends = function () {
        // Making sortable
        var pos_bgn = 0;
        var url = 'friends_position' + '/';

        $( ".friends_business, .friends_nonprofit" ).sortable({
            start: function(event, ui) { 
                pos_bgn = ui.item.index();
            },
            stop: function(event, ui) {
                /*
                console.log("New position: " + ui.item.index());
                console.log("Old position: " + pos_bgn);
                console.log("ID: " + get_int(ui.item[0].id));
                */
                
                if (ui.item.index() != pos_bgn) {
                    make_request({
                        url:url,
                        data: {
                            friend_id:get_int(ui.item[0].id),
                            position_bgn:pos_bgn,
                            position_end:ui.item.index()
                        },
                        callback: function() {
                        }
                    });
                }
            }
        });
        $( ".friends_business, .friends_nonprofit" ).disableSelection();
}

