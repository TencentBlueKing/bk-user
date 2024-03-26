# Generated by Django 3.2.20 on 2023-11-25 01:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalSetting',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(choices=[('tenant_visible', '租户可见性')], max_length=64, primary_key=True, serialize=False, verbose_name='配置唯一标识')),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='配置名称')),
                ('value', models.JSONField(default=dict, verbose_name='配置项')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]