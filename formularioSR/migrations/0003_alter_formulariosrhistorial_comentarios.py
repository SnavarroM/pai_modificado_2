# Generated by Django 4.1 on 2022-09-14 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formularioSR', '0002_formulariosrhistorial_formulariosrderivacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formulariosrhistorial',
            name='comentarios',
            field=models.TextField(null=True, verbose_name='Respuesta'),
        ),
    ]