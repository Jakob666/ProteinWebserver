# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-10 07:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('human_cancer_pro', '0006_refseq'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='refseq',
            table='human_ref2uni',
        ),
    ]
