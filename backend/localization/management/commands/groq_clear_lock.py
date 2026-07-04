from django.core.cache import cache
from django.core.management.base import BaseCommand

from localization.services.groq_translation import HANDLERS
from localization.services.groq_translation_progress import groq_progress_key
from localization.services.groq_translation_runner import (
    groq_result_key,
    release_groq_lock,
)


class Command(BaseCommand):
    help = 'Groq çeviri kilidi ve ilerleme önbelleğini temizler (takılı %0 için).'

    def add_arguments(self, parser):
        parser.add_argument(
            'handler',
            nargs='?',
            choices=sorted(HANDLERS.keys()),
            help='Belirli işleyici; boş bırakılırsa hepsi temizlenir.',
        )

    def handle(self, *args, **options):
        handler = options.get('handler')
        handlers = [handler] if handler else sorted(HANDLERS.keys())
        for name in handlers:
            release_groq_lock(name)
            cache.delete(groq_progress_key(name))
            cache.delete(groq_result_key(name))
            self.stdout.write(f'Temizlendi: {name}')
        self.stdout.write(self.style.SUCCESS('Groq önbellek kilidi temizlendi.'))
