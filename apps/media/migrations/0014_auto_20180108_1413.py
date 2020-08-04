# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-01-08 14:13
from __future__ import unicode_literals

import apps.media.models
import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0013_auto_20180108_1201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='photo',
            field=models.ImageField(storage=django.core.files.storage.FileSystemStorage(location='/home/vamsi/Projects/src/office2017.whistle.it/media_private'), upload_to=apps.media.models.get_upload_photo_path, verbose_name='image'),
        ),
    ]
