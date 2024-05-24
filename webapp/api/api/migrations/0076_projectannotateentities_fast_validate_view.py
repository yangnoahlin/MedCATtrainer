# Generated by Django 2.2.28 on 2024-05-24 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0075_auto_20240429_1350'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectannotateentities',
            name='fast_validate_view',
            field=models.BooleanField(default=False, help_text='An option that limits the context visibible to the user, used for fast review of performance of the underlying model. Shouldbe used in the scenario with an already fine-tuned model.'),
        ),
    ]
