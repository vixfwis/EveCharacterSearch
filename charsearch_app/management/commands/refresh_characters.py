import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.timezone import now
from charsearch_app.models import Character, CharSkill, Skill, Thread
from charsearch_app.tasks.refresh import refresh_characters

logger = logging.getLogger("charsearch.refresh_characters")


class Command(BaseCommand):
    help = "Rescrape eveboard for characters that have threads updated in the last X days"

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            action='store',
            type=int,
            dest='limit',
            default=1,
            required=True,
            help='Refresh characters with threads updated in the last X days')
        parser.add_argument(
            '--staleness',
            action='store',
            type=int,
            dest='staleness',
            default=5,
            help='Required number of days since the last refresh')

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
        refresh_characters(options['limit'], options['staleness'])
