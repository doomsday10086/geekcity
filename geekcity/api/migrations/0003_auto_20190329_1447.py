# Generated by Django 2.1.7 on 2019-03-29 06:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20190329_1446'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='teachers',
        ),
        migrations.AddField(
            model_name='course',
            name='teachers',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='api.Teacher', verbose_name='课程讲师'),
            preserve_default=False,
        ),
    ]
