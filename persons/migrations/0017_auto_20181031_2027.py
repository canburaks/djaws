# Generated by Django 2.0.5 on 2018-10-31 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0016_auto_20181031_1929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='relations',
            field=models.ManyToManyField(blank=True, related_name='_person_relations_+', to='persons.Person'),
        ),
    ]