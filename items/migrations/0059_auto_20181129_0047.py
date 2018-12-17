# Generated by Django 2.0.5 on 2018-11-28 21:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0058_auto_20181125_2004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='movie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='rates', to='items.Movie'),
        ),
        migrations.AlterField(
            model_name='rating',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='rates', to='persons.Profile'),
        ),
    ]
