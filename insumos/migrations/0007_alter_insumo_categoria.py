# Generated by Django 4.1 on 2022-08-12 15:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('insumos', '0006_alter_insumo_categoria_alter_insumo_unidad_medida'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insumo',
            name='categoria',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fkcateg', to='insumos.categoria', verbose_name='Categoría'),
        ),
    ]
