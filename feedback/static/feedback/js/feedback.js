$(document).ready(function(){

    var form = $('#feedback-form');

    var sentAnimationDiv = '<div class="circle-loader"><div class="checkmark draw"></div></div>';

    function sendFeedback() {
        $.ajax({
            url : form.attr('action'),
            type : form.attr('method'),
            data : form.serialize(),

            success : function(result) {
                if (result) {
                    $("#feedback-body").addClass('row h-100 justify-content-center align-items-center');
                    $('.circle-loader').toggleClass('load-complete');
                    $('.checkmark').toggle();
                } else {
                    $("#feedback-body").html('<h2 class="text-danger text-center">' +
                                             '<i class="fas fa-exclamation-triangle fa-3x"></i></h2>')
                }

            }
        });
    }

    form.on('submit', function(event){
        event.preventDefault();
        sendFeedback();
        $("#feedback-body").html(sentAnimationDiv);
    });

});