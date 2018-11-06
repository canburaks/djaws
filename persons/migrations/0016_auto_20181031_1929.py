# Generated by Django 2.0.5 on 2018-10-31 16:29

from django.db import migrations, models
import persons.models


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0015_auto_20181031_1914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='job',
            field=models.CharField(blank=True, choices=[('d', 'Director'), ('a', 'Actor/Actress'), ('w', 'Writer')], max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='relations',
            field=models.ManyToManyField(blank=True, null=True, related_name='_person_relations_+', to='persons.Person'),
        ),
        migrations.AlterField(
            model_name='personimage',
            name='image',
            field=models.ImageField(upload_to=persons.models.person_image_upload_path),
        ),
        migrations.AlterField(
            model_name='personimage',
            name='info',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='follow_director',
            field=models.ManyToManyField(blank=True, related_name='follower', to='persons.Person'),
        ),
    ]