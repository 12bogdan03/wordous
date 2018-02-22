from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

from tasks.models import Task


class Notification(models.Model):
    NEW = 'new'
    READ = 'read'

    STATUS_CHOICES = (
        (NEW, 'нове'),
        (READ, 'прочитане'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL,
                             null=True)
    status = models.CharField(max_length=4, choices=STATUS_CHOICES,
                              default=NEW)
    title = models.CharField(max_length=50)
    text = models.CharField(max_length=150)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)

    def get_absolute_url(self):
        return reverse('notifications:detail', args=[self.id])
