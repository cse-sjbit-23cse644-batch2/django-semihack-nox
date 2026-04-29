from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone

from .models import Participant, Event, EventUpdate, ScheduleItem
from .forms import RegistrationForm, FeedbackForm, EventUpdateForm, ScheduleItemForm
from .utils import generate_pdf, generate_qr_base64, send_registration_email, send_certificate_email


# ── Landing / Event Brochure ──────────────────────────────────────────────────

def landing(request):
    events = Event.objects.all().order_by('-date').prefetch_related('schedule', 'updates')
    featured = events.first()
    qr_data = None
    if featured:
        target_url = featured.event_url if featured.event_url else request.build_absolute_uri(f'/event/{featured.pk}/')
        qr_data = generate_qr_base64(target_url)
    return render(request, 'events/landing.html', {
        'events': events,
        'featured': featured,
        'qr_data': qr_data,
    })


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    schedule = event.schedule.all()
    updates = event.updates.all()[:10]
    target_url = event.event_url if event.event_url else request.build_absolute_uri(f'/event/{event.pk}/')
    qr_data = generate_qr_base64(target_url)
    return render(request, 'events/event_detail.html', {
        'event': event,
        'schedule': schedule,
        'updates': updates,
        'qr_data': qr_data,
    })


# ── Registration ──────────────────────────────────────────────────────────────

def register(request, pk=None):
    event = get_object_or_404(Event, pk=pk) if pk else Event.objects.filter(is_active=True).first()
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            participant = form.save()
            send_registration_email(participant, request)
            messages.success(request,
                f"Registration successful! A confirmation has been sent to {participant.email}.")
            return redirect('register_success', token=participant.token)
    else:
        initial = {'event': event} if event else {}
        form = RegistrationForm(initial=initial)
    return render(request, 'events/register.html', {'form': form, 'event': event})


def register_success(request, token):
    participant = get_object_or_404(Participant, token=token)
    qr_data = generate_qr_base64(
        request.build_absolute_uri(f'/event/{participant.event.pk}/')
    )
    return render(request, 'events/register_success.html', {
        'participant': participant,
        'qr_data': qr_data,
    })


# ── Live Event Updates (AJAX poll) ────────────────────────────────────────────

def live_updates(request, pk):
    event = get_object_or_404(Event, pk=pk)
    updates = list(event.updates.values('id', 'title', 'message', 'posted_at', 'is_important'))
    for u in updates:
        u['posted_at'] = u['posted_at'].strftime('%b %d, %I:%M %p')
    schedule = list(event.schedule.values('id', 'time', 'title', 'speaker', 'is_current'))
    for s in schedule:
        s['time'] = s['time'].strftime('%I:%M %p')
    return JsonResponse({'updates': updates, 'schedule': schedule})


# ── Admin Dashboard ───────────────────────────────────────────────────────────

@staff_member_required
def admin_dashboard(request):
    events = Event.objects.prefetch_related('participants', 'updates', 'schedule')
    participants = Participant.objects.select_related('event').order_by('-registered_at')
    update_form = EventUpdateForm()
    schedule_form = ScheduleItemForm()
    return render(request, 'events/admin_dashboard.html', {
        'participants': participants,
        'events': events,
        'update_form': update_form,
        'schedule_form': schedule_form,
    })


@staff_member_required
@require_POST
def post_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    form = EventUpdateForm(request.POST)
    if form.is_valid():
        update = form.save(commit=False)
        update.event = event
        update.save()
        return JsonResponse({
            'id': update.id,
            'title': update.title,
            'message': update.message,
            'posted_at': update.posted_at.strftime('%b %d, %I:%M %p'),
            'is_important': update.is_important,
        })
    return JsonResponse({'error': 'Invalid form'}, status=400)


@staff_member_required
@require_POST
def toggle_attendance(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    participant.attendance = not participant.attendance
    participant.save(update_fields=['attendance'])
    return JsonResponse({'attendance': participant.attendance, 'pk': pk})


@staff_member_required
@require_POST
def verify_transaction(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    participant.transaction_verified = not participant.transaction_verified
    participant.save(update_fields=['transaction_verified'])
    return JsonResponse({'transaction_verified': participant.transaction_verified, 'pk': pk})


@staff_member_required
@require_POST
def mark_schedule_current(request, pk):
    item = get_object_or_404(ScheduleItem, pk=pk)
    # Unmark all others in same event
    ScheduleItem.objects.filter(event=item.event).update(is_current=False)
    item.is_current = True
    item.save(update_fields=['is_current'])
    return JsonResponse({'ok': True, 'pk': pk})


# ── Feedback ──────────────────────────────────────────────────────────────────

def submit_feedback(request, token):
    participant = get_object_or_404(Participant, token=token)
    if participant.feedback_submitted:
        messages.info(request, "You have already submitted feedback.")
        return redirect('certificate', token=token)
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            participant.feedback_rating = int(form.cleaned_data['rating'])
            participant.feedback_comments = form.cleaned_data.get('comments', '')
            participant.feedback_submitted = True
            participant.save(update_fields=['feedback_rating', 'feedback_comments', 'feedback_submitted'])
            messages.success(request, "Thank you for your feedback!")
            return redirect('certificate', token=token)
    else:
        form = FeedbackForm()
    return render(request, 'events/feedback.html', {'form': form, 'participant': participant})


# ── Certificate ───────────────────────────────────────────────────────────────

def certificate(request, token):
    participant = get_object_or_404(Participant, token=token)
    if not participant.certificate_eligible:
        missing = []
        if not participant.attendance:
            missing.append("Attendance not marked by admin")
        if not participant.feedback_submitted:
            missing.append("Feedback not submitted")
        if not participant.transaction_verified:
            missing.append("Payment not verified by admin")
        return render(request, 'events/certificate_blocked.html',
                      {'participant': participant, 'missing': missing}, status=403)
    # Send certificate email if not sent yet
    if not participant.certificate_sent:
        send_certificate_email(participant, request)
    return generate_pdf(participant)


# ── Stats API ─────────────────────────────────────────────────────────────────

def api_stats(request):
    data = {
        'total_registered': Participant.objects.count(),
        'total_attended': Participant.objects.filter(attendance=True).count(),
        'total_verified': Participant.objects.filter(transaction_verified=True).count(),
        'total_certificates': Participant.objects.filter(
            attendance=True, feedback_submitted=True, transaction_verified=True
        ).count(),
    }
    return JsonResponse(data)
