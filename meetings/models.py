import uuid
from django.db import models


class Meeting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def get_total_votes(self):
        return Participant.objects.filter(meeting=self).count()
    
    def get_best_option(self):
        all_options = list(self.timeslots.all()) + list(self.locations.all())
        if not all_options:
            return None
        
        best = None
        best_score = -1
        
        for option in all_options:
            yes_count = option.votes.filter(choice='yes').count()
            if yes_count > best_score:
                best_score = yes_count
                best = option
        
        return best


class TimeSlot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='timeslots')
    datetime = models.DateTimeField()
    
    class Meta:
        ordering = ['datetime']
    
    def __str__(self):
        return self.datetime.strftime('%a, %d %b %Y, %H:%M')
    
    def get_vote_counts(self):
        return {
            'yes': self.votes.filter(choice='yes').count(),
            'no': self.votes.filter(choice='no').count(),
            'maybe': self.votes.filter(choice='maybe').count(),
        }


class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name
    
    def get_vote_counts(self):
        return {
            'yes': self.votes.filter(choice='yes').count(),
            'no': self.votes.filter(choice='no').count(),
            'maybe': self.votes.filter(choice='maybe').count(),
        }


class Participant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='participants')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['meeting', 'name']
    
    def __str__(self):
        return self.name


class Vote(models.Model):
    CHOICES = [
        ('yes', 'Tak'),
        ('no', 'Nie'),
        ('maybe', 'Może'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='votes')
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    choice = models.CharField(max_length=10, choices=CHOICES)
    
    class Meta:
        unique_together = [
            ['participant', 'timeslot'],
            ['participant', 'location'],
        ]
    
    def __str__(self):
        target = self.timeslot or self.location
        return f"{self.participant.name} - {target}: {self.choice}"
