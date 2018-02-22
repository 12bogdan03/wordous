from django.utils import timezone

from .models import Notification


def create_notification(user, task, title, text):
    new_notification = Notification(
        user=user,
        task=task,
        title=title,
        text=text
    )
    new_notification.save()


def delete_old_notifications():
    Notification.objects.filter(
        created__gte=timezone.now() - timezone.timedelta(days=7)
    ).delete()
