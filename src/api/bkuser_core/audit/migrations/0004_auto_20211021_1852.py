# Generated by Django 3.2.5 on 2021-10-21 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0003_auto_20210516_1652'),
    ]

    operations = [
        migrations.AddField(
            model_name='generallog',
            name='status',
            field=models.CharField(choices=[('succeed', '成功'), ('failed', '失败')], default='successed', max_length=16, verbose_name='状态'),
        ),
    ]
