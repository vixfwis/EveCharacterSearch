import logging
import re
import requests
import json
from dateutil import parser
from bs4 import BeautifulSoup
from django.utils.timezone import now
from charsearch_app.models import Thread, ThreadTitle, Character, CharSkill, NpcCorp, CharStanding, Skill

logger = logging.getLogger("charsearch_app.tasks.scrape")

R_SKILL = re.compile(r"(.+[\w'-]+) / Rank (\d{1,2}) / Level: (\d) / SP: ([\d,]+) of ([\d,]+)")
EVEBOARD_URL = 'https://eveskillboard.com/pilot/%s'
R_PILOT_NAME = r"eveskillboard.com/pilot\/([\w'-]+)"
RS_PWD = [re.compile(r"[pP][wW][\w]*\s*[=\-\:]*\s*([\w]*)"), re.compile(r"[pP][aA][sS][\w]*\s*[=\-\:]*\s*([\w]*)")]
FORUM_URL = 'https://forums.eveonline.com/'
BAZAAR_URL = 'c/marketplace/character-bazaar/l/latest.json?page=%i'
THREAD_URL = 't/%s/%i'


def get_soup(html):
    return BeautifulSoup(html, features="html.parser")


def buildchar(char_dict):
    logger.debug("Building new character, %s" % char_dict['charname'])
    char = Character()
    char.name = char_dict['charname']
    char.total_sp = 0
    char.save()
    for skill in char_dict['skills']:
        char.total_sp += skill[2]
        cs = CharSkill()
        cs.character = char
        cs.level = skill[1]
        cs.skill_points = skill[2]
        base_skill = Skill.objects.filter(name=skill[0]).first()
        if not base_skill:
            logger.warning("Couldn't find skill %s in db, skipping" % skill[0])
            continue
        cs.skill = base_skill
        cs.typeID = base_skill.typeID
        cs.save()
        logger.debug("Created CharSkill for {0}".format(skill))
    for standing in char_dict['standings']:
        corp = NpcCorp.objects.filter(name=standing[0]).first()
        if corp:
            char_standing = CharStanding.objects.create(character=char,corp=corp, value=standing[1])
            char_standing.save()
        else:
            corp = NpcCorp.objects.create(name=standing[0])
            corp.save()
            char_standing = CharStanding.objects.create(character=char, corp=corp, value=standing[1])
            char_standing.save()
            logger.info('Created new npc corp {0}'.format(standing[0]))
    char.last_update = now()
    char.unspent_skillpoints = char_dict['stats']['unallocated_sp']
    char.remaps = char_dict['stats']['remaps']
    char.password = char_dict['password'] or ''
    char.save()
    logger.debug("Character built {0}".format(char_dict['charname']))
    return char


def get_password_soup(s, charname, password=None):
    response = s.get(EVEBOARD_URL % charname)
    pass_required = False
    if response.status_code == 200:
        if 'password' in response.url:
            pass_required = True
        soup = get_soup(response.content)
        if pass_required:
            if password is None:
                return None, None
            token = soup.select('input[name="_token"]')[0]['value']
            response = s.post(response.url, data={
                '_token': token,
                'passwordSend': password
            })
            if response.status_code == 200:
                return get_soup(response.content), password
            else:
                logger.warning('Failed to access passworded eveboard page of %s' % charname)
        else:
            return soup, None
    else:
        return None, None


def parse_stats(soup):
    def get_td(x):
        return x.select('td')[1].text.strip().replace(',', '')
    data = {
        'unallocated_sp': 0,
        'remaps': 0,
        'ss': 0.0
    }
    for tr in soup.select('tr'):
        if 'Unallocated SP'.lower() in tr.text.lower():
            data['unallocated_sp'] = int(get_td(tr))
        if 'Yearly Remap'.lower() in tr.text.lower():
            try:
                data['unallocated_sp'] = int(get_td(tr))
            except ValueError:
                pass  # no yearly remap
        if 'Bonus Remaps'.lower() in tr.text.lower():
            data['remaps'] += int(get_td(tr))
        if 'Security Status'.lower() in tr.text.lower():
            data['ss'] = float(get_td(tr))
    return data


def parse_skills(soup):
    skills = []
    for skill in soup.select('div.skills tr.known_skill'):
        skill = skill.text.strip()
        skill_match = R_SKILL.match(skill)
        if skill_match:
            skill_name = skill_match.group(1)
            level = int(skill_match.group(3))
            sp = int(skill_match.group(4).replace(',', ''))
            skills.append((skill_name, level, sp))
        else:
            logger.warning("Couldn't parse skill string: %s" % skill)
    return skills


def parse_standings(soup):
    standings = []
    for header in soup.select('div.tab-pane h4'):
        if 'Corporation Standings'.lower() in header.text.strip().lower():
            s_table = header.parent.parent.select('tbody.standings')
            if s_table:
                for standing_row in s_table[0].select('tr'):
                    standings.append((standing_row('td')[0].text, float(standing_row('td')[1].text)))
            break
    return standings


def scrape_character(s, charname, password=None):
    logger.debug("Scraping eveboard skills for {0}".format(charname))
    main_soup, actual_password = get_password_soup(s, charname, password=password)
    if main_soup:
        data = {
            'charname': charname,
            'password': actual_password
        }
        # grab all the skills
        skills = parse_skills(main_soup)
        if skills:
            data['skills'] = skills
            stats = parse_stats(main_soup.select('div.panelz')[0])
            data['stats'] = stats
            if stats is None:
                logger.warning("Couldn't get stats for %s" % charname)
            logger.debug("Scraping eveboard for {0} finished, have {1} skills".format(charname, len(skills)))
            logger.debug("Scraping eveboard standings for {0}".format(charname))
            standings = parse_standings(main_soup)
            if len(standings) > 0:
                logger.debug("Parsing standings for {0} suceeded".format(charname))
            else:
                logger.debug("Got skills but couldn't get standings for {0}".format(charname))
            data['standings'] = standings
            return data
    else:
        logger.debug("Scraping eveboard for {0} failed".format(charname))
        return None


def scrape_thread(s, thread):
    logger.debug("Scraping thread {0}".format(thread))
    response = s.get(FORUM_URL + THREAD_URL % (thread['slug'], thread['thread_id']))
    if response.status_code == 200:
        thread_soup = get_soup(response.content)
    else:
        logger.warning('Failed to get thread with id %i, status %i' % (thread['id'], response.status_code))
        return None
    first_post = thread_soup.select('div.post')[0]
    eveboard_link = first_post.find('a', href=re.compile('.*eveskillboard.com/pilot/.*'))
    if eveboard_link:
        logger.debug("Found eveboard link {0}".format(eveboard_link))
        pilot_name = eveboard_link['href'].split('/pilot/')[1]
        # clean up tags and bbcode
        for a in first_post('a'):
            a.extract()
        for img in first_post('img'):
            img.extract()
        first_post = first_post.prettify().replace('<br />', ' ').replace('\n', '').replace('<i>', '').replace(
            '</i>', '').replace('<b>', '').replace('</b>', '')
        # find them passwords!
        passwords = []
        for regs in RS_PWD:
            potential_passwords = regs.finditer(first_post)
            for match in potential_passwords:
                if match.group(1) not in passwords:
                    logger.debug("Found eveboard password {0}".format(match.group(1)))
                    passwords.append(match.group(1))
        if passwords:
            passwords.append('1234')  # append the most commonly used password
            for password in passwords:
                scraped_info = scrape_character(s, pilot_name, password)
                if scraped_info:
                    return scraped_info
                else:
                    return None
        else:
            logger.debug("No passwords found trying without")
            scraped_info = scrape_character(s, pilot_name, None)
            if scraped_info:
                return scraped_info
            else:
                return None
    else:
        logger.debug("Could not find eveboard link")
        return None


def get_bazaar_page(s, pagenumber):
    logger.debug("Scraping grabbing bazaar page {0}".format(pagenumber))
    threads = []
    response = s.get(FORUM_URL + BAZAAR_URL % pagenumber)
    if response.status_code == 200:
        page_data = json.loads(response.content, encoding='utf-8')
    else:
        logger.warning('Failed to get bazaar page %i, status %i' % (pagenumber, response.status_code))
        return threads
    for thread in page_data['topic_list']['topics']:
        title = thread['title']
        thread_id = thread['id']
        slug = thread['slug']
        last_post = parser.parse(thread['last_posted_at'])
        threads.append({
            'title': title,
            'thread_id': thread_id,
            'last_post': last_post,
            'slug': slug
        })
        logger.debug("Found thread title : {0} | threadID : {1}".format(title.rstrip(), thread_id))
    return threads


def scrape_eveo(page_range):
    session = requests.Session()
    threads = []
    for x in page_range:
        threads.extend(get_bazaar_page(session, x))
    for thread in threads:
        existing_thread = Thread.objects.filter(thread_id=thread['thread_id']).first()
        if existing_thread:
            if existing_thread.last_update != thread['last_post']:
                existing_thread.last_update = thread['last_post']
            if existing_thread.thread_title != thread['title']:
                old_title = ThreadTitle(
                    thread=existing_thread,
                    title=existing_thread.thread_title,
                    date=now()
                )
                old_title.save()
                existing_thread.thread_title = thread['title']
                existing_thread.thread_slug = thread['slug']
            existing_thread.save()
        else:
            t = Thread(
                thread_id=thread['thread_id'],
                last_update=thread['last_post'],
                thread_text='',
                thread_title=thread['title'],
                thread_slug=thread['slug'],
            )
            char_dict = scrape_thread(session, thread)
            if char_dict:
                logger.debug("Got character for thread {0}".format(thread['thread_id']))
                t.blacklisted = False
                character = buildchar(char_dict)
                t.character = character
                t.save()
            else:
                logger.debug("Failed to get character for thread, blacklisting".format(thread))
                t.blacklisted = True
                t.save()
