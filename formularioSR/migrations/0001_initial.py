# Generated by Django 4.1 on 2022-09-09 20:29

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('departamentos', '0002_alter_departamento_options_and_more'),
        ('cargos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormularioSR',
            fields=[
                ('id_formulario', models.AutoField(primary_key=True, serialize=False)),
                ('folioSR', models.CharField(max_length=50, verbose_name='Folio SR')),
                ('tipo_formulario', models.CharField(choices=[('', 'Seleccione Tipo Formulario'), ('SOLICITUD', 'SOLICITUD'), ('RECLAMO', 'RECLAMO')], max_length=50, verbose_name='Tipo Formulario')),
                ('rut_solicitante', models.CharField(max_length=50, verbose_name='Rut Solicitante')),
                ('anexo', models.IntegerField(default=0, verbose_name='Anexo')),
                ('email', models.EmailField(max_length=50, verbose_name='Email')),
                ('fecha_ingreso', models.DateField(default=datetime.date.today, verbose_name='Fecha Ingreso')),
                ('hora_ingreso', models.TimeField(verbose_name='Hora Ingreso')),
                ('fecha_respuesta', models.DateField(default=datetime.date.today, verbose_name='Fecha Respuesta')),
                ('comentarios', models.TextField(verbose_name='Comentarios')),
                ('estado', models.BooleanField(default=True, verbose_name='Estado')),
                ('id_cargo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cargos.cargo', verbose_name='Cargo')),
                ('id_departamento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='departamentos.departamento', verbose_name='Departamento')),
                ('id_sub_departamento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='departamentos.subdepartamento', verbose_name='Sub Departamento')),
                ('id_unidad', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='departamentos.unidad', verbose_name='Unidad')),
            ],
        ),
    ]
