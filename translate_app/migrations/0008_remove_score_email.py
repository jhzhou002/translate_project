# Generated by Django 4.2.15 on 2024-11-18 12:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('translate_app', '0007_score_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='score',
            name='email',
        ),
    ]
