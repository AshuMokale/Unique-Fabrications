# Generated by Django 4.2.5 on 2023-11-23 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fabrics', '0002_alter_customuser_user_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Services',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=500)),
            ],
        ),
    ]
