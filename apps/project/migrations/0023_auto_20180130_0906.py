# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-01-30 09:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0022_auto_20180124_1627'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={'get_latest_by': 'date_create', 'ordering': ['-date_last_modify'], 'permissions': (('list_activity', 'can list activity'), ('detail_activity', 'can detail activity'), ('disable_activity', 'can disable activity')), 'verbose_name': 'activity', 'verbose_name_plural': 'activities'},
        ),
        migrations.AlterModelOptions(
            name='project',
            options={'get_latest_by': 'date_create', 'ordering': ['-date_last_modify'], 'permissions': (('list_project', 'can list project'), ('detail_project', 'can detail project'), ('disable_project', 'can disable project')), 'verbose_name': 'project', 'verbose_name_plural': 'projects'},
        ),
        migrations.AlterModelOptions(
            name='task',
            options={'get_latest_by': 'date_create', 'ordering': ['-date_last_modify'], 'permissions': (('list_task', 'can list task'), ('detail_task', 'can detail task'), ('disable_task', 'can disable task')), 'verbose_name': 'task', 'verbose_name_plural': 'tasks'},
        ),
        migrations.AlterModelOptions(
            name='team',
            options={'get_latest_by': 'date_create', 'ordering': ['-date_last_modify'], 'permissions': (('list_team', 'can list team'), ('detail_team', 'can detail team'), ('disable_team', 'can disable team')), 'verbose_name': 'team', 'verbose_name_plural': 'teams'},
        ),
    ]
