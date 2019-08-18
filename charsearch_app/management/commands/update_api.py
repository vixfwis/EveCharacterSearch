import logging
import sqlite3
from django.core.management.base import BaseCommand
from charsearch_app.models import Skill
logger = logging.getLogger("charsearch_app.update_api")


class Command(BaseCommand):
    help = "Used for updating internal db from EVE SDE"

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
        update_skills()


def update_skills():
    print('Updating skills')
    ship_query = open('charsearch_app/tasks/get_skills.sql').read()
    conn = sqlite3.connect('sqlite-latest.sqlite')
    c = conn.cursor()
    created_count = 0
    affected_count = 0
    for row in c.execute(ship_query):
        skill, created = Skill.objects.update_or_create(
            typeID=row[0],
            defaults={
                'name': row[1],
                'rank': row[2],
                'description': row[3],
                'groupName': row[4],
                'groupID': row[5],
                'published': row[6]
            }
        )
        if created:
            created_count += 1
        affected_count += 1
    conn.commit()
    print('%i rows affected, %i new skills added' % (affected_count, created_count))
