from django.core.management.base import BaseCommand

from core.services.astro_rebuild import trigger_astro_rebuild


class Command(BaseCommand):
    help = 'Astro frontend rebuild tetikler (webhook + opsiyonel yerel build)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            default='management_command',
            help='Tetikleyici kaynağı (log için)',
        )
        parser.add_argument(
            '--sync',
            action='store_true',
            help='Arka plan thread yerine senkron çalıştır',
        )

    def handle(self, *args, **options):
        trigger_astro_rebuild(
            source=options['source'],
            async_run=not options['sync'],
        )
        self.stdout.write(self.style.SUCCESS('Astro rebuild tetiklendi'))
