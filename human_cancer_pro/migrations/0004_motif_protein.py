# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-09 07:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('human_cancer_pro', '0003_auto_20180809_1449'),
    ]

    operations = [
        migrations.CreateModel(
            name='Motif',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cancer_type', models.CharField(max_length=10)),
                ('protein_id', models.CharField(max_length=30)),
                ('protein_length', models.IntegerField()),
                ('modification', models.CharField(max_length=30)),
                ('modify_position', models.IntegerField()),
                ('motif_seq', models.CharField(max_length=20)),
                ('start', models.IntegerField()),
                ('end', models.IntegerField()),
            ],
            options={
                'db_table': 'motif_table',
            },
        ),
        migrations.CreateModel(
            name='Protein',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('protein_id', models.CharField(max_length=20)),
                ('sequence', models.TextField()),
            ],
            options={
                'db_table': 'protein_sequence',
            },
        ),
    ]
