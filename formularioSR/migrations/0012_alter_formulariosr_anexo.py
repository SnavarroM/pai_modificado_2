# Generated by Django 4.1 on 2023-04-24 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formularioSR', '0011_alter_formulariosr_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formulariosr',
            name='anexo',
            field=models.IntegerField(default=0, null=True, verbose_name='Anexo'),
        ),
    ]
