import os

from django.db import models
from django.conf import settings
from django.dispatch import receiver


class WorkerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='worker_profile')
    languages = models.CharField(max_length=250, verbose_name='Мови')
    about = models.TextField(max_length=500, blank=True, null=True,
                             verbose_name='Про себе')
    card_number = models.CharField(max_length=20, verbose_name='Номер карти')
    photo = models.ImageField(upload_to='photos/', blank=True, null=True,
                              verbose_name='Фото')

    def get_photo(self):
        if self.photo:
            return self.photo.url
        else:
            return settings.STATIC_URL + 'img/default_avatar.jpg'

    def __str__(self):
        return 'Профіль виконавця {}'.format(self.user.username)


@receiver(models.signals.post_delete, sender=WorkerProfile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `WorkerProfile` object is deleted.
    """
    if instance.photo:
        try:
            if os.path.isfile(instance.photo.path):
                os.remove(instance.photo.path)
        except ValueError:
            return False


@receiver(models.signals.pre_save, sender=WorkerProfile)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `WorkerProfile` object is updated
    with new photo.
    """
    if not instance.pk:
        return False

    try:
        old_photo = WorkerProfile.objects.get(pk=instance.pk).photo
    except WorkerProfile.DoesNotExist:
        return False

    new_photo = instance.photo
    if not old_photo == new_photo:
        try:
            if os.path.isfile(old_photo.path):
                os.remove(old_photo.path)
        except ValueError:
            return False
