from celery.task import task, periodic_task
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from django.contrib.auth.models import User

from tasks.models import Task
from .utils import create_notification, delete_old_notifications

logger = get_task_logger(__name__)


@task(name="create_notification_task")
def create_notification_task(user_id, task_id, title, text):
    """creates notification for user"""

    user = User.objects.filter(pk=user_id)
    task_obj = Task.objects.filter(pk=task_id)

    logger.info("Created notification for user '{}'".format(user.username))

    return create_notification(user, task_obj, title, text)


@periodic_task(
    run_every=(crontab(minute=0, hour='*/6')),
    name="delete_old_notifications_task",
    ignore_result=True
)
def delete_old_notifications_task():
    """deletes notifications, older than 7 days, every 6 hours"""

    delete_old_notifications()
    logger.info("Deleted old notifications")
