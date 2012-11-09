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

