# Generated by Django 4.1.7 on 2023-03-25 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_post_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profileimg',
            field=models.ImageField(blank=True, null=True, upload_to='profile_images'),
        ),
    ]