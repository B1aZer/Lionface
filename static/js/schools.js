$(function() {
    var options = {
        url: "/schools/add/",
        type: "POST",
        dataType: "JSON",
        clearForm: true,
        beforeSubmit: function(formData, jqForm, options) {
            if ($(jqForm[0]).valid()) {
                return true;
            }
            return false;
        },
        success: function(data) {
            console.log($("#show_message"));
            if (data.status === 'OK') {
                $("#show_message").text("Thank you for submitting a school. We will review it as soon as possible.").show().delay(30000).fadeOut();
            } else {
                $("#show_message").text("An error has occured.").show().delay(30000).fadeOut();
            }
            $("#add_school").hide();
        }
    };
    $("#add_school form").validate({
        errorPlacement: function(error, element) {
            return true;
        },
        highlight: function(element) {
            $(element).addClass("error");
        },
        unhighlight: function(element) {
            $(element).removeClass("error");
        }
    });
    $("#add_school form").ajaxForm(options);
});
