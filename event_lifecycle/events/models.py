import uuid
from django.db import models
from django.utils import timezone
from .validators import validate_receipt_file


class Event(models.Model):
    name = models.CharField(max_length=200)
    tagline = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=300)
    venue_address = models.TextField(blank=True)
    organizer = models.CharField(max_length=200, default='SJBIT')
    banner_color = models.CharField(max_length=7, default='#1a3c8f')
    registration_deadline = models.DateField(null=True, blank=True)
    max_participants = models.PositiveIntegerField(default=200)
    is_active = models.BooleanField(default=True)
    event_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    @property
    def qr_target_url(self):
      if self.event_url:
            return self.event_url
            return f"/event/{self.pk}/"

    @property
    def registered_count(self):
        return self.participants.count()

    @property
    def spots_left(self):
        return max(0, self.max_participants - self.registered_count)


class ScheduleItem(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='schedule')
    time = models.TimeField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    speaker = models.CharField(max_length=200, blank=True)
    is_current = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'time']

    def __str__(self):
        return f"{self.time} - {self.title}"


class EventUpdate(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='updates')
    title = models.CharField(max_length=200)
    message = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)
    is_important = models.BooleanField(default=False)

    class Meta:
        ordering = ['-posted_at']

    def __str__(self):
        return f"{self.event.name} - {self.title}"


class Participant(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    student_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    college = models.CharField(max_length=200, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')

    # Transaction
    transaction_id = models.CharField(max_length=100, unique=True)
    receipt = models.FileField(upload_to='receipts/', validators=[validate_receipt_file])
    transaction_verified = models.BooleanField(default=False)

    # Status
    attendance = models.BooleanField(default=False)
    feedback_submitted = models.BooleanField(default=False)
    feedback_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    feedback_comments = models.TextField(blank=True)

    # Email tracking
    confirmation_sent = models.BooleanField(default=False)
    certificate_sent = models.BooleanField(default=False)

    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.student_id})"

    @property
    def certificate_eligible(self):
        return self.attendance and self.feedback_submitted and self.transaction_verified
class Registration(models.Model):
    participant = models.ForeignKey('Participant', on_delete=models.CASCADE)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    attended = models.BooleanField(default=False)
    feedback_submitted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.participant} - {self.event}"