# Generated by Django 2.1.2 on 2018-10-31 16:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("challenges", "0014_auto_20181023_1413")]

    operations = [
        migrations.RemoveField(
            model_name="challenge", name="allow_unfiltered_page_html"
        )
    ]
