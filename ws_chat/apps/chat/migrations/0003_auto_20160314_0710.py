# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_messages_dt'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('dt', models.DateTimeField(auto_created=True)),
                ('message', models.CharField(max_length=255)),
                ('session_key', models.CharField(max_length=32)),
            ],
        ),
        migrations.RemoveField(
            model_name='messages',
            name='admin_user',
        ),
        migrations.DeleteModel(
            name='Messages',
        ),
    ]
