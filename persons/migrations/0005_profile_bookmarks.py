# Generated by Django 2.0.5 on 2018-10-22 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0014_auto_20181022_1901'),
        ('persons', '0004_auto_20181022_1738'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='bookmarks',
            field=models.ManyToManyField(to='items.Movie'),
        ),
    ]