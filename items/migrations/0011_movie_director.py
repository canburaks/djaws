# Generated by Django 2.0.5 on 2018-10-22 15:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0004_auto_20181022_1738'),
        ('items', '0010_auto_20181022_1829'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='director',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='persons.Person'),
        ),
    ]