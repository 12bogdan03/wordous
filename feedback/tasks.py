from celery.task import task
from celery.utils.log import get_task_logger

from .utils import send_feedback_email

logger = get_task_logger(__name__)


@task(name="send_feedback_email_task")
def send_feedback_email_task(subject, email, message):
    """sends feedback email"""

    logger.info("Sent feedback from {}".format(email))

    return send_feedback_email(subject, email, message)
