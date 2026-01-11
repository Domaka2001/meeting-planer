from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
from django.utils import timezone
from .models import Meeting, TimeSlot, Location, Participant, Vote


def home(request):
    return render(request, 'meetings/home.html')


def dashboard(request):
    meetings = Meeting.objects.all().order_by('-created_at')
    return render(request, 'meetings/dashboard.html', {'meetings': meetings})


def create_meeting(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not name:
            return render(request, 'meetings/create.html', {'error': 'Nazwa spotkania jest wymagana'})
        
        meeting = Meeting.objects.create(name=name, description=description)
        
        timeslots = request.POST.getlist('timeslots[]')
        for ts in timeslots:
            if ts.strip():
                try:
                    parsed_datetime = datetime.fromisoformat(ts.strip())
                    if timezone.is_naive(parsed_datetime):
                        parsed_datetime = timezone.make_aware(parsed_datetime)
                    TimeSlot.objects.create(meeting=meeting, datetime=parsed_datetime)
                except (ValueError, TypeError):
                    pass
        
        locations = request.POST.getlist('locations[]')
        for loc in locations:
            if loc.strip():
                Location.objects.create(meeting=meeting, name=loc.strip())
        
        return redirect('meeting_success', meeting_id=meeting.id)
    
    return render(request, 'meetings/create.html')


def meeting_success(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    return render(request, 'meetings/success.html', {'meeting': meeting})


@require_http_methods(["POST"])
def delete_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    meeting.delete()
    return redirect('dashboard')


def meeting_vote(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    timeslots = meeting.timeslots.all()
    locations = meeting.locations.all()
    
    for ts in timeslots:
        ts.counts = ts.get_vote_counts()
    for loc in locations:
        loc.counts = loc.get_vote_counts()
    
    return render(request, 'meetings/vote.html', {
        'meeting': meeting,
        'timeslots': timeslots,
        'locations': locations,
    })


@require_http_methods(["POST"])
def submit_vote(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    name = request.POST.get('name', '').strip()
    
    if not name:
        timeslots = meeting.timeslots.all()
        locations = meeting.locations.all()
        for ts in timeslots:
            ts.counts = ts.get_vote_counts()
        for loc in locations:
            loc.counts = loc.get_vote_counts()
        return render(request, 'meetings/vote.html', {
            'meeting': meeting,
            'timeslots': timeslots,
            'locations': locations,
            'error': 'Podaj swoje imię'
        })
    
    participant, created = Participant.objects.get_or_create(meeting=meeting, name=name)
    
    for ts in meeting.timeslots.all():
        choice = request.POST.get(f'timeslot_{ts.id}')
        if choice in ['yes', 'no', 'maybe']:
            Vote.objects.update_or_create(
                participant=participant,
                timeslot=ts,
                defaults={'choice': choice}
            )
    
    for loc in meeting.locations.all():
        choice = request.POST.get(f'location_{loc.id}')
        if choice in ['yes', 'no', 'maybe']:
            Vote.objects.update_or_create(
                participant=participant,
                location=loc,
                defaults={'choice': choice}
            )
    
    return redirect('meeting_results', meeting_id=meeting.id)


def meeting_results(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    timeslots = meeting.timeslots.all()
    locations = meeting.locations.all()
    participants = meeting.participants.all()
    
    for ts in timeslots:
        ts.counts = ts.get_vote_counts()
        ts.participant_votes = []
        for p in participants:
            vote = Vote.objects.filter(participant=p, timeslot=ts).first()
            ts.participant_votes.append({'name': p.name, 'choice': vote.choice if vote else None})
    
    for loc in locations:
        loc.counts = loc.get_vote_counts()
        loc.participant_votes = []
        for p in participants:
            vote = Vote.objects.filter(participant=p, location=loc).first()
            loc.participant_votes.append({'name': p.name, 'choice': vote.choice if vote else None})
    
    best_option = meeting.get_best_option()
    best_option_counts = None
    if best_option:
        best_option_counts = best_option.get_vote_counts()
    
    return render(request, 'meetings/results.html', {
        'meeting': meeting,
        'timeslots': timeslots,
        'locations': locations,
        'participants': participants,
        'best_option': best_option,
        'best_option_counts': best_option_counts,
    })


@require_http_methods(["POST"])
def add_timeslot_field(request):
    return HttpResponse('''
        <div class="timeslot-field flex items-center gap-2 mb-2">
            <input type="datetime-local" name="timeslots[]" class="flex-1 px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
            <button type="button" onclick="this.parentElement.remove()" class="text-red-500 hover:text-red-700 p-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
            </button>
        </div>
    ''')


@require_http_methods(["POST"])
def add_location_field(request):
    return HttpResponse('''
        <div class="location-field flex items-center gap-2 mb-2">
            <input type="text" name="locations[]" placeholder="np. Biuro główne, Sala konferencyjna A" class="flex-1 px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
            <button type="button" onclick="this.parentElement.remove()" class="text-red-500 hover:text-red-700 p-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
            </button>
        </div>
    ''')
