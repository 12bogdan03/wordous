$(document).ready(function(){

    var checkNotifications = function() {
        $.ajax({
            url: $("#notificationsUrl").attr("data-notifications-url"),
            type: 'GET',

            success: function (data) {
                if (data.new) {
                    $('.indicator').html('<i class="fas fa-fw fa-circle"></i>');
                    dropdwnheader.text('Нові сповіщення:').removeClass('py-0');
                    divider.addClass('dropdown-divider');
                    $('#notifications-list').html(data.notifications);
                } else {
                    $('.indicator').empty();
                    dropdwnheader.empty().addClass('py-0');
                    divider.removeClass('dropdown-divider');
                    $('#notifications-list').html('<small class="dropdown-item text-muted text-center">Нових сповіщень немає</small>');
                }
            }
        });
    };

    var dropdwnheader = $('h6.dropdown-header');
    var divider = dropdwnheader.next();

    checkNotifications();
    setInterval(checkNotifications, 60000);

    $('#notificationsDropdown').parent().on('hide.bs.dropdown', function () {
        var notificationPks = [];

        $("input[name='notification-pk']").each(function(){
            notificationPks.push(Number($(this).val()));
        });

        $.ajax({
            url: $("#notificationsUrl").attr("data-notifications-url"),
            type: "POST",
            data: {'notificationPks[]': notificationPks},
            success: function (data) {
                $('.indicator').empty();
                dropdwnheader.empty().addClass('py-0');
                divider.removeClass('dropdown-divider');
                $('#notifications-list').html('<small class="dropdown-item text-muted text-center">Нових сповіщень немає</small>');
            }
        });

    });
});