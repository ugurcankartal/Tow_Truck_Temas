# core uygulamasından içerik modellerini kaldırır (tablolar content uygulamasında kalır).

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
        ('core', '0006_content_zones_and_site_images'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name='SiteImagePlacement'),
                migrations.DeleteModel(name='SiteImage'),
                migrations.DeleteModel(name='ContentZone'),
            ],
            database_operations=[],
        ),
    ]
