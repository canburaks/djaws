# Generated by Django 2.0.5 on 2018-10-31 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0022_auto_20181031_2030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movieimage',
            name='info',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]
