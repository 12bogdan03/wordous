from django.utils import timezone

from .models import Task


def delete_old_tasks():
    Task.objects.filter(
        modified__gte=timezone.now() - timezone.timedelta(days=30),
        status=Task.DONE
    ).delete()
