# Generated by Django 3.2.8 on 2021-11-17 06:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Stream',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('whois', models.CharField(blank=True, max_length=100, null=True)),
                ('pps', models.IntegerField(blank=True, null=True)),
                ('source', models.CharField(max_length=50)),
                ('group', models.CharField(max_length=50)),
                ('udp_port', models.CharField(blank=True, max_length=50, null=True)),
                ('active', models.BooleanField(default=True)),
                ('last_found', models.DateTimeField(auto_now_add=True)),
                ('report_count', models.IntegerField(default=0)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stream_set', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Description',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=10000)),
                ('votes', models.IntegerField(default=0)),
                ('stream', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='view.stream')),
                ('user_submitted', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='description_set', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]