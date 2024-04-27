# Generated by Django 4.2.11 on 2024-04-16 15:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('monemome', '0003_delete_userprofile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='balance',
        ),
        migrations.RemoveField(
            model_name='category',
            name='transaction_type',
        ),
        migrations.AddField(
            model_name='account',
            name='purpose',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='account',
            name='user',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='category',
            name='user',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Transaction',
        ),
    ]
