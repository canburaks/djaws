# Generated by Django 2.0.5 on 2019-01-04 14:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0039_follow_typeof'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='follow_lists',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='follow_persons',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='follow_topics',
        ),
        migrations.AlterField(
            model_name='follow',
            name='liste',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='followers', to='items.List'),
        ),
        migrations.AlterField(
            model_name='follow',
            name='person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='followers', to='persons.Person'),
        ),
        migrations.AlterField(
            model_name='follow',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='followers', to='items.Topic'),
        ),
    ]
