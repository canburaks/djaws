# Generated by Django 2.0.5 on 2019-01-22 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0074_auto_20190122_0146'),
    ]

    operations = [
        migrations.AddField(
            model_name='list',
            name='public',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='list',
            name='movies',
            field=models.ManyToManyField(blank=True, null=True, related_name='lists', to='items.Movie'),
        ),
        migrations.AlterField(
            model_name='list',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='list',
            name='summary',
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
    ]