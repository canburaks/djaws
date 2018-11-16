# Generated by Django 2.0.5 on 2018-11-14 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0041_auto_20181111_0014'),
        ('persons', '0021_profile_follow_persons'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='follow_lists',
            field=models.ManyToManyField(blank=True, related_name='followers', to='items.List'),
        ),
    ]
