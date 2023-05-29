# Generated by Django 4.1 on 2023-05-02 21:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('departamentos', '0008_alter_subdepartamento_options_alter_unidad_options'),
        ('formularioSR', '0012_alter_formulariosr_anexo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formulariosr',
            name='id_sub_departamento',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='departamentos.subdepartamento', verbose_name='Sub Departamento'),
        ),
        migrations.AlterField(
            model_name='formulariosr',
            name='id_unidad',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='departamentos.unidad', verbose_name='Unidad'),
        ),
    ]
