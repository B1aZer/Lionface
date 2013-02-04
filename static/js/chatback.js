$(document).ready(function() {
    var socket = io.connect("/chat");
    socket.emit('join', LionFace.User.username); 

    var ChatModel = Backbone.Model.extend({
        });

    // The view that reprsents an individual chat line
    var ChatItem = Backbone.View.extend({
        render: function(){
            // grab the handlebars.js template we defined for this view
            //var template = Handlebars.compile($("#chat_item_template").html());

            // render the template out with the model as a context
            //this.$el.html(template(this.model.toJSON()));
            this.$el.html('<span>'+  this.model.toJSON().chat_line + '</span>');

            // always return this for easy chaining
            return this;
        },
    });

    // The view that represents our chat form
    var ChatView = Backbone.View.extend({

        // handle the form submit event and fire the method "send"
        events: {
            "keypress #chat_input": "send",
            "click .chat_div": "showchat"
        },

        // constructor of the view
        initialize: function() {
            var me = this;

            // when a new chat event is emitted, add the view item to the DOM
            socket.on("chat", function(data) {
            console.log(data);

                // create the view and pass it the new model for context
                var chat_item = new ChatItem({
                    model: new ChatModel({
                        chat_line: data.message
                    })
                });

                // render it to the DOM
                $(".user_content").append(chat_item.render().el);
            });
        },

        showchat: function(e) {
            var $this = $(this);
            var toggled = $this.data('toggled');
            if (!toggled) {
                $('.user_conatiner').show();
                $this.data('toggled',true);
            }
            else {
                $('.user_conatiner').hide();
                $this.data('toggled',false);
            }
        },

        send: function(evt) {
            //evt.preventDefault();
            if (evt.keyCode == 13) {
                var $this = $(this);
                var username = $('.chat_username').val();
                var val = $("#chat_input").val();

                socket.emit("user message",username, val);

                $("#chat_input").val("");
            }

        },

        render: function(){
            //var template = Handlebars.compile($("#chat_template").html());
            //$(this.el).html(template());
        },

    });

/*
    // Backbone.js router
    var Router = Backbone.Router.extend({
        // Match urls with methods
        routes: {
            "": "index"
        },

        index: function() {
            var view = new ChatView({
                el: $(".user_conatiner"),
            });
            console.log('view');
            view.render();
        }

    });
    */

    var view = new ChatView({
                el: $("#main_chat_div"),
            });
    //view.render();
    // start backbone routing
    //var router = new Router();
    //Backbone.history.start({ pushState: true });

})
