"""
python manage.py seed
Seeds a full SJBIT Hackathon event with schedule, updates, and participants.
"""
import datetime
from django.core.management.base import BaseCommand
from events.models import Event, ScheduleItem, EventUpdate, Participant


class Command(BaseCommand):
    help = 'Seed database with SJBIT Hackathon event data'

    def handle(self, *args, **kwargs):
        # Create event
        event, _ = Event.objects.get_or_create(
            name='HackSJBIT 2025',
            defaults={
                'tagline': 'Build. Innovate. Disrupt.',
                'description': (
                    'HackSJBIT is SJBIT\'s flagship 24-hour hackathon where students from across '
                    'Karnataka come together to solve real-world problems using technology. '
                    'Compete for prizes worth ₹1,00,000, get mentored by industry experts, '
                    'and build something that matters. Open to all engineering students.'
                ),
                'date': datetime.date(2025, 6, 15),
                'start_time': datetime.time(9, 0),
                'end_time': datetime.time(9, 0),  # next day
                'venue': 'SJBIT Main Auditorium & Labs',
                'venue_address': 'Sri Jayachamarajendra College of Engineering, Mysore Road, Bangalore - 560060',
                'organizer': 'SJBIT',
                'max_participants': 200,
                'registration_deadline': datetime.date(2025, 6, 10),
            }
        )

        # Schedule
        schedule_items = [
            (datetime.time(8, 30), 'Registration & Check-in', 'Collect your kit and badge at the main entrance', '', 1),
            (datetime.time(9, 0), 'Inauguration Ceremony', 'Welcome address by Principal & Chief Guest', 'Dr. Rajesh Kumar', 2),
            (datetime.time(9, 30), 'Problem Statement Release', 'Teams receive their challenge domains', '', 3),
            (datetime.time(10, 0), 'Hacking Begins!', '24-hour coding marathon starts now', '', 4),
            (datetime.time(13, 0), 'Lunch Break', 'Networking lunch provided for all participants', '', 5),
            (datetime.time(15, 0), 'Mentor Round 1', 'Industry mentors visit teams for guidance', 'Various', 6),
            (datetime.time(18, 0), 'Progress Check', 'Mid-point evaluation by judges', '', 7),
            (datetime.time(20, 0), 'Dinner & Networking', 'Dinner + fun activities', '', 8),
            (datetime.time(0, 0), 'Midnight Snacks', 'Keep the energy up!', '', 9),
            (datetime.time(6, 0), 'Final Stretch', 'Last 3 hours — polish your projects', '', 10),
            (datetime.time(9, 0), 'Submission Deadline', 'All projects must be submitted', '', 11),
            (datetime.time(10, 0), 'Project Presentations', 'Teams present to judges (5 min each)', '', 12),
            (datetime.time(14, 0), 'Results & Prize Distribution', 'Winners announced + certificates', '', 13),
            (datetime.time(15, 0), 'Valedictory & Closing', 'Closing ceremony and group photo', '', 14),
        ]

        for time, title, desc, speaker, order in schedule_items:
            ScheduleItem.objects.get_or_create(
                event=event, title=title,
                defaults={'time': time, 'description': desc, 'speaker': speaker, 'order': order}
            )

        # Sample updates
        updates = [
            ('Registration Open!', 'Online registration is now open. Register before June 10 to secure your spot!', False),
            ('Team Formation', 'Teams of 2-4 members. Solo participants will be grouped. Register now!', False),
            ('Prizes Announced', '1st Prize: ₹50,000 | 2nd Prize: ₹30,000 | 3rd Prize: ₹20,000 + goodies for all!', True),
        ]
        for title, msg, important in updates:
            EventUpdate.objects.get_or_create(
                event=event, title=title,
                defaults={'message': msg, 'is_important': important}
            )

        # Participants
        samples = [
            ('1SJ21CS001', 'Alice Reyes', 'alice@sjbit.edu.in', True, True, True, 5),
            ('1SJ21CS002', 'Bob Santos', 'bob@sjbit.edu.in', True, True, False, None),
            ('1SJ21CS003', 'Cara Lim', 'cara@sjbit.edu.in', False, False, False, None),
            ('1SJ21EC001', 'David Kumar', 'david@sjbit.edu.in', True, False, False, None),
        ]

        for sid, name, email, attended, verified, feedback, rating in samples:
            p, created = Participant.objects.get_or_create(
                student_id=sid,
                defaults={
                    'name': name, 'email': email,
                    'event': event,
                    'transaction_id': f'TXN-{sid}',
                    'receipt': 'receipts/sample.pdf',
                    'attendance': attended,
                    'transaction_verified': verified,
                    'feedback_submitted': feedback,
                    'feedback_rating': rating,
                    'college': 'SJBIT',
                    'phone': '9876543210',
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created: {p}'))
            else:
                self.stdout.write(f'  Skipped: {p}')

        self.stdout.write(self.style.SUCCESS('\nSeed complete! Visit http://127.0.0.1:8000/'))
