$(document).ready(function(){
    $("label[id=Worker]").click(function(){
        $("#profile_form").slideDown('200ms');
    });

    $("label[id=Client]").click(function(){
        $("#profile_form").slideUp('200ms');
    });

    // check passwords match
    function checkPasswordMatch() {
        var password1 = $("#id_password1").val();
        var password2 = $("#id_password2").val();

        if (password1 !== password2) {
            $("#id_password1, #id_password2").addClass("is-invalid");
            $("#passwordMatchError").html("<div class=\"alert alert-warning text-center\" role=\"alert\">\n" +
                "  Паролі не збігаються\n" +
                "</div>");
            $("#registerBtn").prop("disabled", true).css('cursor', 'not-allowed');

        } else {
            $("#id_password1, #id_password2").removeClass("is-invalid");
            $("#passwordMatchError").empty();
            $("#registerBtn").prop("disabled", false).css('cursor', 'default');
        }

    }
    $("#id_password1, #id_password2").keyup(checkPasswordMatch);

    // check username available and equals regex
    $("#id_username").change(function () {
        var form = $(this).closest("form");

        // var re = /[\w\d@.+\-_]{1,150}/;
        // if (re.test(this.value)) {
        //     $("#registerBtn").prop('disabled', false);
        // } else {
        //     $("#registerBtn").prop('disabled', true);
        // }

        $.ajax({
            url: form.attr("data-validate-username-url"),
            data: form.serialize(),
            dataType: 'json',
            success: function (data) {
                if (data.is_taken) {
                    $("#username-not-available").html(data.error_message);
                } else {
                    $("#username-not-available").empty();
                }
            }
        });
    });

    // check email available
    $("#id_email").change(function () {
        var form = $(this).closest("form");

        $.ajax({
            url: form.attr("data-validate-email-url"),
            data: form.serialize(),
            dataType: 'json',
            success: function (data) {
                if (data.is_taken) {
                    $("#email-not-available").html(data.error_message);
                } else {
                    $("#email-not-available").empty();
                }
            }
        });
    });

    // file upload
    $('#file-selector').on('change', function() {
        var fileName = $(this).val().split('\\').pop();
        $('#upload-file-info').html(fileName);
    });

    // characters remaining countdown
    var maxLength = $("#id_about").attr("maxlength");
    $('#remaining-chars').text(maxLength);
    $("#id_about").keyup(function() {
        var length = $(this).val().length;
        var length = maxLength-length;
        $('#remaining-chars').text(length);
    });

    $("#langTags").tagit({
        availableTags: languages,
        caseSensitive: false,
        singleField: true,
        singleFieldNode: $('#id_languages')
    });

});