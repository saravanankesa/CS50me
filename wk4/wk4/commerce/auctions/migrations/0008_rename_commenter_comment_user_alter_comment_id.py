# Generated by Django 5.0.3 on 2024-03-29 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0007_remove_listing_active_usermessage"),
    ]

    operations = [
        migrations.RenameField(
            model_name="comment",
            old_name="commenter",
            new_name="user",
        ),
        migrations.AlterField(
            model_name="comment",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]