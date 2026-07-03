from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteimage',
            name='image',
            field=models.ImageField(
                blank=True,
                help_text='Yüklü görsel varsa API ve sitede bu kullanılır.',
                upload_to='site_images/%Y/%m/',
                verbose_name='Yüklenen görsel',
            ),
        ),
        migrations.AlterField(
            model_name='siteimage',
            name='image_url',
            field=models.URLField(
                blank=True,
                help_text='Yüklü görsel yoksa bu URL kullanılır.',
                max_length=500,
                verbose_name='Görsel URL',
            ),
        ),
    ]
