from celery.task import periodic_task
from celery.schedules import crontab
from celery.utils.log import get_task_logger

from .utils import delete_old_tasks

logger = get_task_logger(__name__)


@periodic_task(
    run_every=(crontab(minute=0, hour=0)),
    name="delete_old_tasks_task",
    ignore_result=True
)
def delete_old_tasks_task():
    """
    deletes tasks that are older than 7 days and
    have status 'DONE', every day at midnight
    """

    delete_old_tasks()
    logger.info("Deleted old tasks")
