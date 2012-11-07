LionFace.Pages.Settings = function() {
    this.runner();
}


LionFace.Pages.Settings.prototype = {

    runner : function() {
        this.bind_functions();

    },

    //Binding
    bind_functions : function() {

    $(document).on('click','#delete_page', function (e) {
        e.preventDefault();
        $('#delete_page_form').show().attr('style','display:inline');
        $('#submit_button').hide();
        $(this).hide();
        $('#id_confirm_pass').focus();
    });    

    },
}

$(function() {         
});

