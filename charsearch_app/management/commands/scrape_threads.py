import logging
from django.core.management import BaseCommand

from charsearch_app.tasks.scrape import scrape_eveo

logger = logging.getLogger("charsearch_app.scrape_threads")


class Command(BaseCommand):
    help = "Scrape the forums for new sale threads and to update old threads"

    def add_arguments(self, parser):
        parser.add_argument(
            '--pages',
            action='store',
            type=int,
            dest='pages',
            default=1,
            help='The number of pages of the bazaar to scrape')
        parser.add_argument('--start', action='store', type=int, dest='start', default=0, help='The starting page')

    def handle(self, *args, **options):
        verbosity = options.get('verbosity')
        if verbosity == 0:
            logger.setLevel(logging.WARN)
        elif verbosity == 1:  # default
            logger.setLevel(logging.INFO)
        elif verbosity > 1:
            logger.setLevel(logging.DEBUG)
        if verbosity > 2:
            logger.setLevel(logging.DEBUG)
        scrape_eveo(range(options['start'], options['start'] + options['pages']))
