# Generated by Django 3.2.20 on 2023-08-07 03:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataSourcePlugin',
            fields=[
                ('id', models.CharField(max_length=128, primary_key=True, serialize=False, verbose_name='数据源插件唯一标识')),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='数据源插件名称')),
                ('description', models.TextField(blank=True, default='', verbose_name='描述')),
                ('logo', models.TextField(blank=True, default='', null=True, verbose_name='Logo')),
            ],
        ),
        migrations.CreateModel(
            name='DataSource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='数据源名称')),
                ('owner_tenant_id', models.CharField(db_index=True, max_length=64, verbose_name='归属租户')),
                ('plugin_config', models.JSONField(default=dict, verbose_name='数据源插件配置')),
                ('sync_config', models.JSONField(default=dict, verbose_name='数据源同步任务配置')),
                ('field_mapping', models.JSONField(default=dict, verbose_name='用户字段映射')),
                ('plugin', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='data_source.datasourceplugin')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]