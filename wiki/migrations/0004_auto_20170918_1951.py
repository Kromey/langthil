# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-09-18 19:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0003_auto_20170918_1950'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='markdown',
            field=models.TextField(help_text='Formatted using Markdown', verbose_name='article content'),
        ),
    ]
