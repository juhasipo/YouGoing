from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from yougoing.utils.security import generate_random_string
from datetime import datetime, date, time
from django.db.models.fields.related import ForeignKey
    
def map_values(model, initial=None):
    if initial == None:
        initial = {}
    for field_name in model._meta.get_all_field_names():
        field = model._meta.get_field(field_name)
        value = field.value_to_string(model)
        initial[field_name] = value
        print "%s: %s" % (field_name, value)
    return initial

    
PARTICIPATION_YES = 1
PARTICIPATION_MAYBE = 2
PARTICIPATION_NO = 3

class Anonynous_participant(models.Model):
    name = models.CharField(max_length=63)
    
class EventDetails(models.Model):
    address = models.CharField(max_length=255)
    coordinate = models.CharField(max_length=32)
    description = models.CharField(max_length=2047)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class EventParticipationStatus(models.Model):
    participant = models.ForeignKey(User)
    anonymous = models.ForeignKey(Anonynous_participant)
    is_going = models.IntegerField() # 1 = YES, 2 = MAYBE, 3 = NO
    reason = models.CharField(max_length=2047)
    
class SubEventInstance(models.Model):
    participants = models.ManyToManyField(EventParticipationStatus)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    class Meta:
        ordering = ['-start_time']
    
    def has_started(self):
        now = datetime.now()
        return now > self.start_time
    
    def add_or_change_status(self, user, status, message = None):
        try:
            existing_participation = self.objects.get(user_username=user.username)
            existing_participation.status = status
            existing_participation.message = message
            existing_participation.save()
        except ObjectDoesNotExist:
            participation = EventParticipationStatus(participant=user, is_going=status, reason=message)
            participation.save()
            self.participants.add(participation)
            self.save()

REPEAT_NONE = 0           
REPEAT_WEEKLY = 1
REPEAT_MONTHLY = 2
REPEAT_ANNUALLY = 3

REPEAT_CHOISES = (
    (REPEAT_NONE, "No repearing"),
    (REPEAT_WEEKLY, "Weekly"),
    (REPEAT_MONTHLY, "Monthly"),
    (REPEAT_ANNUALLY, "Annually"),
)

NONEDAY = 10
MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6

REPEAT_CHOISES = (
    (NONEDAY, "No repeat"),
    (MONDAY, "Monday"),
    (TUESDAY, "Tuesday"),
    (WEDNESDAY, "Wednesday"),
    (THURSDAY, "Thursday"),
    (FRIDAY, "Friday"),
    (SATURDAY, "Saturday"),
    (SUNDAY, "Sunday"),
)

class SubEvent(models.Model):
    # First datetime event occures
    start_date = models.DateField()
    start_time = models.TimeField()
    # Last datetime event occures
    end_date = models.DateField()
    end_time = models.TimeField()
    #repeat_times = models.IntegerField()
    repeat_type = models.IntegerField()
    day_of_week = models.IntegerField(blank=True, null=True)
    linked_subevents = models.ManyToManyField("self")
    instances = models.ManyToManyField(SubEventInstance)
    
    class Meta:
        ordering = ['start_date', 'day_of_week']
    
    def modify(self):
        # End this event set
        # Create new set untill end
        pass
    def get_next_event(self):
        try:
            return self.instances.all()[0]
        except Exception:
            return None
    
    
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
    event_poll = models.ForeignKey(EventPoll, blank=True, null=True)

    @staticmethod
    def get_user_events(user):
        return Event.objects.filter(creator=user)

    def event_to_dict(self):
        d = {}
        d["name"] = self.name
        d["description"] = self.details.description
        d["address"] = self.details.address
        d["coordinate"] = self.details.coordinate
        d["secrey_key"] = self.secret_key
        d["is_public"] = self.is_public
        d["start_date"] = self.sub_events.all()[0].start_date
        d["start_time"] = self.sub_events.all()[0].start_time
        d["end_date"] = self.sub_events.all()[0].end_date
        d["end_time"] = self.sub_events.all()[0].end_time
        return d

    @staticmethod
    def get_event(event_id, user, secret_key):
        try:
            event = Event.objects.get(id=event_id)
            if event is not None and event.can_view(user, secret_key):
                return event
        except ObjectDoesNotExist:
            return None
        return None
    
    @staticmethod
    def create_event(creator, form):
        name = form.cleaned_data["name"]
        print "Creating new event with name %s" % name
        event = Event(creator=creator, name=name)
        details = EventDetails(address=form.cleaned_data["address"],\
                               description=form.cleaned_data["description"],\
                               coordinate=form.cleaned_data["coordinates"])
        details.save()
        
        event.details = details
        event.secret_key = generate_random_string(12, 12, True)
        event.save()
        
        sub_event_args = Event.get_values_from_form(["start_date", "start_time", "end_date", "end_time"], form)
        sub_event_args["repeat_type"] = REPEAT_NONE
        sub_event_args["day_of_week"] = NONEDAY
        sub_event = SubEvent(**sub_event_args)
        sub_event.save()
        event.sub_events.add(sub_event)
        sub_event.save()
        
        return event
    
    @staticmethod
    def get_values_from_form(values, form):
        kwargs = {}
        for value in values:
            cd = form.cleaned_data[value]
            kwargs[value] = cd
        return kwargs
    

    def get_next_event(self):
        current_datetime = datetime.now()
        current_date = date.today()

        current_day_of_week = current_datetime.weekday()
        
        this_week_active_events=SubEvent.objects\
            .filter(start_time__lt=current_date,\
                    end_time__gt=current_date).order_by('day_of_week')
        # Try to find closest by weekday
        first_event_of_week = None # Next event this week
        next_event_not_this_week = None # Next event next week or later
        for event in this_week_active_events:
            if event.start_date <= current_date and \
               event.start_time < current_datetime.time():
                if event.day_of_week >= current_day_of_week:
                    first_event_of_week = event
                elif event.day_of_week < current_day_of_week:
                    next_event_not_this_week = event
        if first_event_of_week is not None:
            return first_event_of_week
        return next_event_not_this_week

    def get_next_event_instance(self):
        event = self.get_next_event()
        if event.has_started():
            pass
        else:
            return event
        # If event has been started, create new event
        #  
        return None
    
    def get_poll(self):
        return None
    def create_poll(self):
        return None
    
    def can_view(self, user, secret_key):
        if self.is_public:
            return True
        if secret_key != None and self.secret_key == secret_key:
            return True
        if self.creator.username == user.username:
            return True
        if user in self.modifiers:
            return True
        if user in self.invited_users:
            return True
        return False
    

            
    
    