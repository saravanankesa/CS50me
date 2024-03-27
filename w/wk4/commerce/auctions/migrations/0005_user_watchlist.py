# Generated by Django 5.0.3 on 2024-03-27 23:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0004_listing_is_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="watchlist",
            field=models.ManyToManyField(
                blank=True, related_name="watchlisted_by", to="auctions.listing"
            ),
        ),
    ]
