# Generated by Django 2.0.5 on 2018-10-22 15:25

from django.db import migrations, models
import django_mysql.models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0008_auto_20181022_1813'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movie',
            name='ratings',
        ),
        migrations.AddField(
            model_name='movie',
            name='ratings_user',
            field=django_mysql.models.SetTextField(models.IntegerField(), default=set(), max_length=15, size=None),
        ),
    ]
