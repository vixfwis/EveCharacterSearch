import logging
from datetime import timedelta

import requests
from django.db.models import Q
from django.utils.timezone import now
from charsearch_app.models import Thread, Character, CharSkill
from charsearch_app.tasks.scrape import scrape_character

logger = logging.getLogger("charsearch_app.tasks.refresh")


def refresh_characters(limit, staleness):
    session = requests.Session()
    staledate = now() - timedelta(days=staleness)
    update_limit = now() - timedelta(days=limit)
    updated_threads = Thread.objects.filter(last_update__gte=update_limit, blacklisted=False)
    stale_characters = Character.objects.filter(
        Q(last_update__lte=staledate) | Q(last_update=None), thread__in=updated_threads)
    for character in stale_characters:
        logger.debug("Updating stale character %s" % character.name)
        scraped_info = scrape_character(session, character.name, character.password)
        if scraped_info:
            new_sp_total = 0
            for skill in scraped_info['skills']:
                existing_skill = character.skills.filter(skill__name=skill[0])
                if len(existing_skill) > 0:
                    existing_skill[0].skill_points = skill[2]
                    existing_skill[0].level = skill[1]
                    new_sp_total += skill[2]
                    existing_skill[0].save()
                else:
                    cs = CharSkill()
                    cs.character = character
                    cs.level = skill[1]
                    cs.skill_points = skill[2]
                    cs.typeID = cs.skill.typeID
                    cs.save()
                    character.skills.add(cs)
                    new_sp_total += skill[2]
            character.remaps = scraped_info['stats']['remaps']
            character.unspent_skillpoints = scraped_info['stats']['unallocated_sp']
            character.total_sp = new_sp_total
            character.last_update = now()
            character.save()
            logger.debug("Update of stale character %s complete" % character.name)
