# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('message', models.CharField(max_length=255)),
                ('session_key', models.CharField(max_length=32)),
                ('admin_user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
