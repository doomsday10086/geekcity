# Generated by Django 2.1.7 on 2019-03-29 06:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20190329_1447'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teacher',
            old_name='brief',
            new_name='describe',
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='role',
        ),
    ]
