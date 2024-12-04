# Generated by Django 4.2.15 on 2024-11-07 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TranslationScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_text', models.TextField()),
                ('translated_text', models.TextField()),
                ('score', models.DecimalField(decimal_places=2, max_digits=5)),
                ('review', models.TextField()),
                ('upload_time', models.DateTimeField(auto_now_add=True)),
                ('year', models.IntegerField()),
            ],
        ),
    ]
