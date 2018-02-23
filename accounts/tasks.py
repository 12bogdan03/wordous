from celery.task import task
from celery.utils.log import get_task_logger
from django.contrib.auth.models import User

from .utils import send_activation_email

logger = get_task_logger(__name__)


@task(name="send_activation_email_task")
def send_activation_email_task(request, user_id):
    """creates notification for user"""

    user = User.objects.get(pk=user_id)

    logger.info("Sent activation email for user '{}'".format(user.username))

    return send_activation_email(request, user)
