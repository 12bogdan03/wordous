from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

import os


class Task(models.Model):
    EDIT = 'ed'
    TRANSLATE = 'tr'

    KIND_CHOICES = (
        (EDIT, 'Редагування'),
        (TRANSLATE, 'Переклад')
    )

    NEW = 'nw'
    IN_PROGRESS = 'ip'
    WAITING_FOR_FEE = 'wff'
    DONE = 'dn'

    STATUS_CHOICES = (
        (NEW, 'Нове'),
        (IN_PROGRESS, 'В роботі'),
        (WAITING_FOR_FEE, 'Очікування оплати'),
        (DONE, 'Готово')
    )

    LANGUAGES = [
        'китайська', 'іспанська', 'англійська',
        'гінді', 'арабська', 'португальська',
        'японська', 'німецька', 'в\'єтнамська',
        'корейська', 'французька', 'турецька',
        'італійська', 'польська', 'російська',
        'українська', 'грецька', 'шведська',
        'нідерландська', 'чеська',
    ]

    kind = models.CharField(max_length=10, choices=KIND_CHOICES,
                            verbose_name='Тип')
    status = models.CharField(max_length=4, choices=STATUS_CHOICES,
                              default=NEW, verbose_name='Статус')
    language = models.CharField(max_length=15, verbose_name='Мова оригіналу')
    translation_language = models.CharField(max_length=15,
                                            blank=True, null=True,
                                            verbose_name='Мова перекладу')
    description = models.TextField(max_length=500, blank=True, null=True,
                                   verbose_name='Опис')
    creator = models.ForeignKey(User, on_delete=models.CASCADE,
                                related_name='creator',
                                verbose_name='Створив')
    executor = models.ForeignKey(User, on_delete=models.CASCADE,
                                 blank=True, null=True,
                                 related_name='executor',
                                 verbose_name='Виконавець')
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Дата створення')
    modified = models.DateTimeField(auto_now=True, verbose_name='Змінено')
    deadline = models.DateTimeField(blank=True, null=True, verbose_name='Дедлайн')
    file = models.FileField(upload_to='files/', verbose_name='Файл')
    solution_file = models.FileField(upload_to='solutions/', blank=True,
                                     null=True, verbose_name='Файл з рішенням')
    solution_preview = models.TextField(null=True, verbose_name='Прев\'ю рішення')
    estimated_price = models.DecimalField(max_digits=6, decimal_places=2,
                                          blank=True, null=True,
                                          verbose_name='Вартість')

    class Meta:
        ordering = ('-created',)
        verbose_name = 'завдання'
        verbose_name_plural = 'завдання'

    def get_absolute_url(self):
        return reverse('tasks:task_detail', args=[self.id])

    def is_expired(self):
        if self.deadline:
            return self.deadline < timezone.now()
        return False

    def file_name(self):
        return os.path.basename(self.file.name)

    def generate_solution_preview(self):
        import docx2txt
        text = docx2txt.process(self.solution_file.file)
        preview_length = int((len(text) * 10)/100)  # 10% of solution file length
        preview = text[:preview_length] + '...'
        self.solution_preview = preview
        self.save()

    def __str__(self):
        return 'Завдання #' + str(self.id)


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name='Завдання')
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                verbose_name='Створив')
    text = models.TextField(max_length=300, verbose_name='Текст')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')

    class Meta:
        ordering = ('-created',)
        verbose_name = 'коментар'
        verbose_name_plural = 'коментарі'

    def __str__(self):
        return 'Коментар #{}'.format(self.id)


@receiver(models.signals.post_delete, sender=Task)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes files from filesystem
    when corresponding `Task` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

    if instance.solution_file:
        if os.path.isfile(instance.solution_file.path):
            os.remove(instance.solution_file.path)


@receiver(models.signals.pre_save, sender=Task)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `Task` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = Task.objects.get(pk=instance.pk).file
    except Task.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        try:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
        except ValueError:
            return False
