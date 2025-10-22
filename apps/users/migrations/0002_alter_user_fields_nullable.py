# Fix nullable fields in User model
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, null=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, help_text='Optional username', max_length=150, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='employee_id',
            field=models.CharField(blank=True, help_text='Employee ID', max_length=50, null=True, unique=True),
        ),
    ]
