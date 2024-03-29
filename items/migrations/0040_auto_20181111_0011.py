# Generated by Django 2.0.5 on 2018-11-10 21:11

from django.db import migrations, models
import django_mysql.models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0039_auto_20181110_2224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='tags',
            field=django_mysql.models.ListTextField(models.CharField(max_length=20), default=[], help_text="Enter the type of video category.\n E.g:'video-essay or interview or conversations'", null=True, size=None),
        ),
    ]
