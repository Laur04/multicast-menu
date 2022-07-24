# Generated by Django 4.0.4 on 2022-07-13 22:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('view', '0009_stream_created_at_stream_updated_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrendingStream',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField()),
                ('stream', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='trending_stream', to='view.stream')),
            ],
        ),
    ]
