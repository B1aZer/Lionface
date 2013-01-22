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
            if (data.status === 'OK') {
                $("#school_list").prepend(data.school);
            } else {
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
