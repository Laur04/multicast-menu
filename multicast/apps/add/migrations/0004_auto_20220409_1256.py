# Generated by Django 3.2.12 on 2022-04-09 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('add', '0003_alter_uploadsubmission_celery_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manualsubmission',
            name='celery_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='uploadsubmission',
            name='celery_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]