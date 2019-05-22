# Generated by Django 2.2.1 on 2019-05-22 00:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_id', models.TextField()),
                ('conversation_id', models.TextField()),
            ],
            options={
                'unique_together': {('channel_id', 'conversation_id')},
            },
        ),
    ]
