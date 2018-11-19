# Generated by Django 2.0.5 on 2018-11-17 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0053_auto_20181117_1916'),
        ('persons', '0022_profile_follow_lists'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='follow_topics',
            field=models.ManyToManyField(blank=True, related_name='followers', to='items.Topic'),
        ),
    ]
