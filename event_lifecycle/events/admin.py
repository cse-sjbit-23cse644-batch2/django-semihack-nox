from django.contrib import admin
from .models import Event, Participant, ScheduleItem, EventUpdate


class ScheduleInline(admin.TabularInline):
    model = ScheduleItem
    extra = 1
    fields = ['order', 'time', 'title', 'speaker', 'description', 'is_current']


class UpdateInline(admin.TabularInline):
    model = EventUpdate
    extra = 1
    fields = ['title', 'message', 'is_important']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'venue', 'registered_count', 'spots_left', 'is_active']
    inlines = [ScheduleInline, UpdateInline]


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['name', 'student_id', 'email', 'event', 'transaction_verified', 'attendance', 'feedback_submitted', 'certificate_eligible']
    list_filter = ['event', 'attendance', 'transaction_verified', 'feedback_submitted']
    search_fields = ['name', 'student_id', 'email', 'transaction_id']
    readonly_fields = ['token', 'registered_at']
    list_editable = ['transaction_verified', 'attendance']


@admin.register(EventUpdate)
class EventUpdateAdmin(admin.ModelAdmin):
    list_display = ['event', 'title', 'posted_at', 'is_important']
    list_filter = ['event', 'is_important']


@admin.register(ScheduleItem)
class ScheduleItemAdmin(admin.ModelAdmin):
    list_display = ['event', 'time', 'title', 'speaker', 'is_current']
    list_filter = ['event']
    list_editable = ['is_current']
