# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-27 12:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0002_auto_20180321_1247'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='allow_unfiltered_page_html',
            field=models.BooleanField(default=False, help_text='If true, the page HTML is NOT filtered, allowing the challenge administrator to have full control over the page contents when they edit it in ckeditor.'),
        ),
    ]
