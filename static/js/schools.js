LionFace.Schools = function(options) {
    this.options = $.extend({
    }, options || {});
    this.init();
};

LionFace.Schools.prototype = {
    init: function() {
        this.add_school();
        this.join_to_school();
    },

    show_school: function(school_id) {
        $(".alum_school").removeClass("school_navON");
        $($("#school_" + school_id)).addClass("school_navON");
        $("#school_name").text($("#school_" + school_id).find(".school_name").text());
        this.current_school = school_id;
    },

    leave_school: function(school_url) {
        var school_year = $(".sub_filter_feedON").text();
        var current_school = this.current_school;
        var data = {school_id: current_school,
            school_year: school_year};
        $.post(school_url, data, function(data) {
            $("#school_" + current_school).remove();
        }, "JSON");
    },

    add_school: function() {
        var options = {
            url: LionFace.Schools.add_school_url,
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
                if (data.status === "OK") {
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
    },

    join_to_school: function() {
        var options = {
            url: LionFace.Schools.join_to_school_url,
            type: "POST",
            dataType: "JSON",
            clearForm: true,
            beforeSubmit: function(formData, jqForm, options) {
                var form = jqForm[0];
                var year = parseInt(form.year.value, 10);
                if (year && !isNaN(year)) {
                    return true;
                }
                $(form.year).addClass("error");
                return false;
            },
            success: function(data) {
                if (data.status === "OK") {
                    $("#alum_schools").append(data.alum_school);
                    $("#school_list #school_" + data.school_id).remove();
                    // $("#school_list #school_" + data.school_id)
                    //     .find(".school_count").text($(data.alum_school)
                    //     .find(".school_count").text());
                } else {
                }
                $(".join_to_school #year").removeClass("error");
            }
        };
        $(".join_to_school").ajaxForm(options);
    }
};

$(function() {
    LionFace.Schools = new LionFace.Schools();
});
