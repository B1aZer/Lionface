LionFace.Pages = function() {
    this.runner();
}


LionFace.Pages.prototype = {

    runner : function() {
        this.bind_functions();

    },

    //Binding
    bind_functions : function() {
    },
}

$(function() {         
    profile_page = new LionFace.Pages()
});
