# Generated by Django 2.0.5 on 2018-10-22 15:00

from django.db import migrations
import django_mysql.models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0005_auto_20181022_1754'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='ratings',
            field=django_mysql.models.JSONField(default=dict, verbose_name={'dummy': set(), 'user': set()}),
        ),
    ]