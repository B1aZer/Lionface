LionFace.Pages = function() {
    this.init();
}


LionFace.Pages.prototype = {

    init : function() {
        var self = this;
        self.bind_functions();
    },

    //Binding
    bind_functions : function() {
    },
}

$(function() {         
    LionFace.Pages = new LionFace.Pages()
});
