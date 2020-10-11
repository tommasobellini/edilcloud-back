# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-03 14:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0013_auto_20171103_1446'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='done',
        ),
        migrations.AddField(
            model_name='activity',
            name='status',
            field=models.CharField(choices=[('to-do', 'to-do'), ('progress', 'progress'), ('completed', 'completed')], default='to-do', max_length=25, verbose_name='status'),
        ),
        migrations.AddField(
            model_name='project',
            name='status',
            field=models.IntegerField(choices=[(0, 'closed'), (1, 'open'), (-1, 'draft')], default=1, verbose_name='status'),
        ),
    ]
