# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-24 09:47
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('user_upload', '0003_auto_20180817_1114'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userfile',
            name='upload_success',
        ),
        migrations.AlterField(
            model_name='userfile',
            name='upload_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 8, 24, 9, 47, 22, 148459, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='userfile',
            name='visit_time',
            field=models.BigIntegerField(default=1535104042.148459),
        ),
    ]
