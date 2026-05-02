# Generated migration to add property_ref as unique field

from django.db import migrations, models


def populate_property_ref(apps, schema_editor):
    """Populate property_ref field with generated values YK0001, YK0002, etc."""
    Properties = apps.get_model('propertylisting', 'Properties')
    for idx, prop in enumerate(Properties.objects.order_by('id'), start=1):
        prop.property_ref = f'YK{idx:04d}'
        prop.save()


class Migration(migrations.Migration):

    dependencies = [
        ('propertylisting', '0006_favorite'),
    ]

    operations = [
        migrations.AddField(
            model_name='properties',
            name='property_ref',
            field=models.CharField(blank=True, editable=False, max_length=10, null=True, unique=True),
        ),
        migrations.RunPython(populate_property_ref),
        migrations.AlterField(
            model_name='properties',
            name='property_ref',
            field=models.CharField(editable=False, max_length=10, unique=True),
        ),
    ]
