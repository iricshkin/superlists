# Generated by Django 4.2.4 on 2023-11-05 18:06

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("lists", "0004_item_list"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="item",
            options={"ordering": ("id",)},
        ),
        migrations.AlterUniqueTogether(
            name="item",
            unique_together={("list", "text")},
        ),
    ]