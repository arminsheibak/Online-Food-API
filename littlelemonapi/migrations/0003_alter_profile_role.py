# Generated by Django 5.0.6 on 2024-06-26 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("littlelemonapi", "0002_alter_order_delivery_crew"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="role",
            field=models.CharField(
                choices=[("C", "customer"), ("D", "delivery_crew"), ("A", "admin")],
                default="C",
                max_length=1,
            ),
        ),
    ]
