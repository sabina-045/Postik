# Generated by Django 2.2.16 on 2023-01-19 10:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0014_auto_20230118_2128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment', to=settings.AUTH_USER_MODEL, verbose_name='Автор комментария'),
        ),
        migrations.DeleteModel(
            name='Follow',
        ),
    ]
