# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-17 03:14
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('user_upload', '0002_auto_20180817_1050'),
    ]

    operations = [
        migrations.AddField(
            model_name='userfile',
            name='visit_time',
            field=models.BigIntegerField(default=1534475666.872878),
        ),
        migrations.AlterField(
            model_name='userfile',
            name='upload_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 8, 17, 3, 14, 26, 872878, tzinfo=utc)),
        ),
    ]
