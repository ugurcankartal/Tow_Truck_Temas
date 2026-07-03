# Mevcut core_* tablolarını content uygulamasına taşır (yalnızca Django state).

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0006_content_zones_and_site_images'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='ContentZone',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('code', models.SlugField(max_length=50, unique=True, verbose_name='Kod')),
                        ('name', models.CharField(max_length=100, verbose_name='Bölüm adı')),
                        ('description', models.TextField(blank=True, verbose_name='Açıklama')),
                    ],
                    options={
                        'verbose_name': 'İçerik bölgesi',
                        'verbose_name_plural': 'İçerik bölgeleri',
                        'db_table': 'core_contentzone',
                        'ordering': ['id'],
                    },
                ),
                migrations.CreateModel(
                    name='SiteImage',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('image_url', models.URLField(max_length=500, verbose_name='Görsel URL')),
                        ('title', models.CharField(max_length=120, verbose_name='Başlık')),
                        ('subtitle', models.CharField(blank=True, help_text='Hero slayt üst satırı.', max_length=200, verbose_name='Alt başlık')),
                        ('description', models.TextField(blank=True, help_text='Scroll-draw alt metni.', verbose_name='Açıklama')),
                        ('alt_text', models.CharField(max_length=200, verbose_name='Görsel alt metni (SEO)')),
                        ('is_active', models.BooleanField(default=True, verbose_name='Aktif')),
                    ],
                    options={
                        'verbose_name': 'Site görseli',
                        'verbose_name_plural': 'Site görselleri',
                        'db_table': 'core_siteimage',
                        'ordering': ['id'],
                    },
                ),
                migrations.CreateModel(
                    name='SiteImagePlacement',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('order', models.PositiveIntegerField(default=0, verbose_name='Sıra')),
                        ('is_active', models.BooleanField(default=True, verbose_name='Aktif')),
                        ('site_image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='placements', to='content.siteimage', verbose_name='Görsel')),
                        ('zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='placements', to='content.contentzone', verbose_name='Bölge')),
                    ],
                    options={
                        'verbose_name': 'Görsel konumu',
                        'verbose_name_plural': 'Görsel konumları',
                        'db_table': 'core_siteimageplacement',
                        'ordering': ['zone', 'order', 'id'],
                    },
                ),
                migrations.AddField(
                    model_name='siteimage',
                    name='zones',
                    field=models.ManyToManyField(related_name='images', through='content.SiteImagePlacement', to='content.contentzone', verbose_name='Gösterim bölgeleri'),
                ),
                migrations.AddConstraint(
                    model_name='siteimageplacement',
                    constraint=models.UniqueConstraint(fields=('site_image', 'zone'), name='unique_image_per_zone'),
                ),
            ],
            database_operations=[],
        ),
    ]
