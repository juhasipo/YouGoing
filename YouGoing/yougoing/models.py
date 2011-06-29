from django.db import models
from django.contrib.auth.models import User

class Anonynous_participant(models.Model):
    name = models.CharField(max_length=63)
    
class EventDetails(models.Model):
    address = models.CharField(max_length=255)
    coordinate = models.CharField(max_length=32)
    description = models.CharField(max_length=2047)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
class SubEventInstance(models.Model):
    participants = models.ManyToManyField(User)
    other_participants = models.ManyToManyField(Anonynous_participant)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
class SubEvent(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    repeat_times = models.IntegerField()
    repeat_type = models.IntegerField()
    repeat_days = models.CommaSeparatedIntegerField(max_length=13)
    modified_subevents = models.ManyToManyField("self")
    modified = models.BooleanField(default=False)
    instances = models.ManyToManyField(SubEventInstance)
    
class AnswerTime(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
class EventPollAnswer(models.Model):
    participant = models.ForeignKey(User)
    times = models.ManyToManyField(AnswerTime)
    
class EventPoll(models.Model):
    duration = models.TimeField()
    deadline = models.DateTimeField()
    answers = models.ManyToManyField(EventPollAnswer)
    
class Event(models.Model):
    name = models.CharField(max_length=255,blank=False)
    creator = models.ForeignKey(User,related_name="event_creator")
    modifiers = models.ManyToManyField(User,related_name="event_modifiers")
    details = models.ForeignKey(EventDetails)
    sub_events = models.ManyToManyField(SubEvent)
    secret_key = models.CharField(max_length=32)
    is_public = models.BooleanField()
    invited_users = models.ManyToManyField(User)
    event_poll = models.ForeignKey(EventPoll)
