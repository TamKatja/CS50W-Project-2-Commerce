# Generated by Django 4.1.3 on 2022-12-07 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0004_alter_listing_image_file"),
    ]

    operations = [
        migrations.AlterField(
            model_name="listing",
            name="image_file",
            field=models.ImageField(
                blank=True,
                default="default_listing_image.png",
                null=True,
                upload_to="images",
            ),
        ),
    ]
