# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_auto_20160314_0710'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='other_session_key',
            field=models.CharField(max_length=32, default=datetime.datetime(2016, 3, 14, 7, 26, 28, 506007, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
