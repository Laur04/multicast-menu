# Generated by Django 4.0.4 on 2022-07-24 14:05

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('view', '0010_trendingstream'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trendingstream',
            options={'ordering': ('-score',)},
        ),
        migrations.AddField(
            model_name='stream',
            name='removed_likes',
            field=models.ManyToManyField(related_name='unliked_streams', to=settings.AUTH_USER_MODEL),
        ),
    ]
