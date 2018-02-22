$(document).ready(function(){

    $("#edit-choice").click(function(){
        $("#translation-language-field").slideUp('200ms');
    });

    $("#translate-choice").click(function(){
        $("#translation-language-field").css('display', 'flex');
    });

    // file upload
    $('#file-selector').on('change', function() {
        var fileName = $(this).val().split('\\').pop();
        $('#upload-file-info').html(fileName);
    });

    // characters remaining countdown
    var maxLength = $("#id_description").attr("maxlength");
    $('#remaining-chars').text(maxLength);
    $("#id_description").keyup(function() {
        var length = $(this).val().length;
        var length = maxLength-length;
        $('#remaining-chars').text(length);
    });

    $("#translationLangTags").tagit({
        availableTags: languages,
        caseSensitive: false,
        singleField: true,
        singleFieldNode: $('#id_translation_language'),
        tagLimit: 1
    });
    $("#originLangTags").tagit({
        availableTags: languages,
        caseSensitive: false,
        singleField: true,
        singleFieldNode: $('#id_language'),
        tagLimit: 1
    });

    flatpickr("#id_deadline", {
        enableTime: true,
        dateFormat: "Y-m-d H:i",
        minDate: "today",
        time_24hr: true,
        locale: 'uk'
    });
});