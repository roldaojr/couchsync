# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Revision',
            fields=[
                ('change_seq', models.AutoField(serialize=False, primary_key=True)),
                ('id', models.CharField(unique=True, max_length=64)),
                ('seq', models.BigIntegerField()),
                ('prev', models.CharField(max_length=64, null=True)),
                ('docid', models.CharField(max_length=64)),
                ('deleted', models.BooleanField(default=False)),
                ('object_id', models.CharField(max_length=64)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
