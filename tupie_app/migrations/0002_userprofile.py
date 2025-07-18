# Generated by Django 5.2.4 on 2025-07-19 17:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tupie_app', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='profiles/')),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('verification_status', models.CharField(choices=[('unverified', 'Unverified'), ('verified', 'Verified User'), ('organization', 'Organization')], default='unverified', max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='userprofile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
