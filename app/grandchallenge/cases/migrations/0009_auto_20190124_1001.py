# Generated by Django 2.1.5 on 2019-01-24 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("cases", "0008_auto_20181207_1142")]

    operations = [
        migrations.RemoveField(model_name="image", name="image_type"),
        migrations.AddField(
            model_name="imagefile",
            name="image_type",
            field=models.CharField(
                choices=[("MHD", "MHD"), ("TIFF", "TIFF")],
                default="MHD",
                max_length=4,
            ),
        ),
    ]
