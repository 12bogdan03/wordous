from django.http import JsonResponse, HttpResponse
from django.views import generic
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Notification


class NewNotificationsView(LoginRequiredMixin, generic.View):
    def get(self, request):
        new_notifications = Notification.objects.filter(
            user=request.user,
            status=Notification.NEW
        )
        new = False
        if new_notifications:
            new = True

        return JsonResponse({
            'new': new,
            'notifications': render_to_string(
                'notifications/notifications_dropdown.html',
                {'notifications': new_notifications})
        }, safe=False)

    def post(self, request):
        notification_pks = request.POST.getlist('notificationPks[]')
        # mark notifications read
        Notification.objects.filter(pk__in=notification_pks).update(
            status=Notification.READ
        )
        return HttpResponse("OK")


class NotificationListView(LoginRequiredMixin, generic.ListView):
    model = Notification
    context_object_name = 'notification_list'
    template_name = 'notifications/notifications_list.html'
    paginate_by = 10

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
