LionFace.Schools = function(options) {
    this.options = $.extend({
    }, options || {});
    this.init();
};

LionFace.Schools.prototype = {
    init: function() {
        this.add_school();
    },

    detail_school: function(detail_url, school_id, school_year) {
        $(".alum_school").removeClass("school_navON");
        $($("#school_" + school_id)).addClass("school_navON");

        var data = {school_id: school_id, school_year: school_year};
        $.post(detail_url, data, function (data) {
            if (data.status === "OK") {
                $("#school").html(data.school);

                $("#school_years a.sub_filter_feedON").removeClass("sub_filter_feedON").addClass("sub_filter_feed");
                $("#school_year_" + school_year).removeClass("sub_filter_feed").addClass("sub_filter_feedON");
            }
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

    join_to_school: function(join_url, form) {
        var options = {
            url: join_url,
            type: "POST",
            dataType: "JSON",
            clearForm: true,
            beforeSubmit: function(formData, jqForm, options) {
                var form = jqForm[0];
                var year = parseInt(form.year.value, 10);
                var today = new Date();
                var yyyy = today.getFullYear();
                if (year && !isNaN(year) && year >= 2000 && year <= yyyy) {
                    return true;
                }
                $(form.year).addClass("error");
                $(form.year).attr("title", "Field empty or Not number or Not in allowed range.");
                return false;
            },
            success: function(data) {
                if (data.status === "OK") {
                    $("#alum_schools").append(data.alum_school);
                    $("#school_list #school_" + data.school_id).remove();
                } else {
                }
                $(".join_to_school #year").removeClass("error");
                $(".join_to_school #year").attr("title", "");
            }
        };
        $(form).ajaxSubmit(options);
    },

    leave_school: function(school_url, school_id) {
        var _this = this;
        var school_year = $(".sub_filter_feedON").text();
        var data = {school_id: school_id,
            school_year: school_year};
        $.post(school_url, data, function (data) {
            if (data.status === 'OK') {
                $("#school_" + school_id).remove();
                $("#school").html("<p>You left School.</p>");
                $("#find").html(data.find_school);
            }
        }, "JSON");
    }
};

$(function() {
    LionFace.Schools = new LionFace.Schools();
});
