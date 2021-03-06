# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-09-18 19:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='page title')),
                ('slug', models.SlugField(unique=True)),
                ('published', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('is_nsfw', models.BooleanField(default=False)),
                ('is_spoiler', models.BooleanField(default=False)),
                ('text', models.TextField(help_text='Formatted using Markdown')),
            ],
        ),
        migrations.DeleteModel(
            name='Page',
        ),
    ]
