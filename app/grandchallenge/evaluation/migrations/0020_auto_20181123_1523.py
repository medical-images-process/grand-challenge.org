# Generated by Django 2.1.3 on 2018-11-23 15:23

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("evaluation", "0019_auto_20181115_1211")]

    operations = [
        migrations.AddField(
            model_name="method",
            name="requires_cpu_cores",
            field=models.DecimalField(
                decimal_places=2, default=Decimal("1.0"), max_digits=4
            ),
        ),
        migrations.AddField(
            model_name="method",
            name="requires_gpu",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="method",
            name="requires_gpu_memory_gb",
            field=models.PositiveIntegerField(default=4),
        ),
        migrations.AddField(
            model_name="method",
            name="requires_memory_gb",
            field=models.PositiveIntegerField(default=4),
        ),
    ]
