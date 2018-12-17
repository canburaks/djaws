# Generated by Django 2.0.5 on 2018-11-28 21:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0023_profile_follow_topics'),
        ('items', '0059_auto_20181129_0047'),
    ]

    operations = [
        migrations.CreateModel(
            name='Prediction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_points', models.IntegerField()),
                ('prediction', models.DecimalField(blank=True, decimal_places=1, max_digits=2, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='predictions', to='items.Movie')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='predictions', to='persons.Profile')),
            ],
        ),
    ]
