# Generated by Django 2.0.5 on 2018-12-04 21:57

from django.db import migrations, models
import persons.models


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0028_auto_20181205_0057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='poster',
            field=models.ImageField(blank=True, upload_to=persons.models.person_poster_upload_path),
        ),
    ]