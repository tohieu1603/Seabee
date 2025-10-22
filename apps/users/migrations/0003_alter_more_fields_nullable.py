# Fix more nullable fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_fields_nullable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='position',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.URLField(blank=True, null=True, help_text='Avatar URL'),
        ),
    ]
