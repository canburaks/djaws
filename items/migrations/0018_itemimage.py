# Generated by Django 2.0.5 on 2018-10-31 15:55

from django.db import migrations, models
import django.db.models.deletion
import items.models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0017_auto_20181031_1828'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('info', models.CharField(max_length=40)),
                ('image', models.ImageField(blank=True, upload_to=items.models.item_image_upload_path)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='items.Movie')),
            ],
        ),
    ]
