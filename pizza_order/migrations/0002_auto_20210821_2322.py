# Generated by Django 3.2.6 on 2021-08-21 23:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pizza_order', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pizzaorder',
            old_name='crust',
            new_name='Crust',
        ),
        migrations.RenameField(
            model_name='pizzaorder',
            old_name='flavor',
            new_name='Flavor',
        ),
        migrations.RenameField(
            model_name='pizzaorder',
            old_name='order_id',
            new_name='Order_ID',
        ),
        migrations.RenameField(
            model_name='pizzaorder',
            old_name='ordered_by',
            new_name='Ordered_By',
        ),
        migrations.RenameField(
            model_name='pizzaorder',
            old_name='size',
            new_name='Size',
        ),
        migrations.RenameField(
            model_name='pizzaorder',
            old_name='table_number',
            new_name='Table_No',
        ),
        migrations.RenameField(
            model_name='pizzaorder',
            old_name='timestamp',
            new_name='Timestamp',
        ),
    ]
