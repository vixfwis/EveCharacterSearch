from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now


class Character(models.Model):
    name = models.CharField(max_length=64, db_index=True)
    total_sp = models.BigIntegerField()
    last_update = models.DateTimeField(default=now)
    password = models.CharField(max_length=64, blank=True)
    unspent_skillpoints = models.IntegerField(default=0)
    remaps = models.IntegerField(default=0)


class NpcCorp(models.Model):
    name = models.CharField(max_length=256)


class CharStanding(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE, related_name='standings')
    corp = models.ForeignKey(NpcCorp, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=4, decimal_places=2)


class Skill(models.Model):
    name = models.CharField(max_length=64)
    typeID = models.IntegerField(db_index=True)
    groupID = models.IntegerField()
    groupName = models.CharField(max_length=64)
    description = models.TextField()
    rank = models.SmallIntegerField()
    published = models.BooleanField(default=False)


class CharSkill(models.Model):
    character = models.ForeignKey('Character', db_index=True, on_delete=models.CASCADE, related_name='skills')
    skill_points = models.IntegerField()
    level = models.IntegerField(db_index=True)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    typeID = models.IntegerField(db_index=True, default=1)

    class Meta:
        index_together = ['typeID', 'level']


class Thread(models.Model):
    last_update = models.DateTimeField(default=now, db_index=True)
    blacklisted = models.BooleanField()
    thread_title = models.TextField()
    thread_id = models.IntegerField()
    thread_slug = models.TextField()
    character = models.ForeignKey('Character', null=True, on_delete=models.CASCADE)


class ThreadTitle(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='title_history')
    title = models.TextField()
    date = models.DateTimeField(default=now)


class RequiredSkill(models.Model):
    typeID = models.IntegerField(db_index=True)
    level = models.IntegerField(db_index=True)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)


class Ship(models.Model):
    name = models.CharField(max_length=100)
    required_skills = models.ManyToManyField('RequiredSkill', related_name='required_by')
    groupID = models.IntegerField(db_index=True)
    groupName = models.CharField(max_length=100)
    itemID = models.IntegerField()
