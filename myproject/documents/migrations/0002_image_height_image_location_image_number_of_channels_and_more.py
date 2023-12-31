# Generated by Django 4.2.4 on 2023-08-13 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='height',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='location',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='number_of_channels',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='width',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='pdf',
            name='location',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='pdf',
            name='num_pages',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='pdf',
            name='page_height',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='pdf',
            name='page_width',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
