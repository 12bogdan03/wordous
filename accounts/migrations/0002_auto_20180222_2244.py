# Generated by Django 2.0.2 on 2018-02-22 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workerprofile',
            name='about',
            field=models.TextField(blank=True, max_length=500, null=True, verbose_name='Про себе'),
        ),
        migrations.AlterField(
            model_name='workerprofile',
            name='card_number',
            field=models.CharField(max_length=20, verbose_name='Номер карти'),
        ),
        migrations.AlterField(
            model_name='workerprofile',
            name='languages',
            field=models.CharField(max_length=250, verbose_name='Мови'),
        ),
        migrations.AlterField(
            model_name='workerprofile',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='photos/', verbose_name='Фото'),
        ),
    ]
