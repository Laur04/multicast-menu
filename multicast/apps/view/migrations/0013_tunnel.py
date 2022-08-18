# Generated by Django 3.2.15 on 2022-08-18 15:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('view', '0012_alter_stream_categories_alter_stream_likes_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tunnel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active_viewer_count', models.BooleanField(default=1)),
                ('amt_gateway_up', models.BooleanField(default=False)),
                ('ffmpeg_up', models.BooleanField(default=False)),
                ('ffmpeg_pid', models.IntegerField(blank=True, null=True)),
                ('filename', models.CharField(max_length=10)),
                ('stream', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tunnel', to='view.stream')),
            ],
        ),
    ]
