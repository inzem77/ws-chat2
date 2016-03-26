# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='messages',
            name='dt',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 26, 15, 54, 57, 567372, tzinfo=utc), auto_created=True),
            preserve_default=False,
        ),
    ]
