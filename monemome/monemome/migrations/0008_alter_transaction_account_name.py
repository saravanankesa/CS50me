# Generated by Django 4.2.11 on 2024-04-18 14:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('monemome', '0007_transaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='account_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='monemome.account'),
        ),
    ]