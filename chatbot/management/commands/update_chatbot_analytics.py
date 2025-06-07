from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Avg
from datetime import timedelta
from chatbot.models import ChatSession, ChatMessage, ChatbotAnalytics, ChatbotFeedback

class Command(BaseCommand):
    help = 'Update daily chatbot analytics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date to analyze (YYYY-MM-DD format). Default is yesterday.',
        )

    def handle(self, *args, **options):
        if options['date']:
            from datetime import datetime
            target_date = datetime.strptime(options['date'], '%Y-%m-%d').date()
        else:
            target_date = (timezone.now() - timedelta(days=1)).date()

        self.stdout.write(f'Updating analytics for {target_date}...')

        # Get sessions for the target date
        sessions = ChatSession.objects.filter(
            created_at__date=target_date
        )

        # Get messages for the target date
        messages = ChatMessage.objects.filter(
            created_at__date=target_date
        )

        # Calculate metrics
        total_sessions = sessions.count()
        total_messages = messages.count()
        unique_users = sessions.filter(user__isnull=False).values('user').distinct().count()
        
        # Calculate resolved queries (sessions with at least one bot response)
        resolved_queries = sessions.filter(
            messages__sender='bot'
        ).distinct().count()

        # Escalated to human (placeholder - implement based on your escalation logic)
        escalated_to_human = 0

        # Average session duration
        session_durations = []
        for session in sessions:
            if session.messages.exists():
                first_msg = session.messages.first()
                last_msg = session.messages.last()
                duration = last_msg.created_at - first_msg.created_at
                session_durations.append(duration)

        avg_duration = None
        if session_durations:
            avg_duration = sum(session_durations, timedelta()) / len(session_durations)

        # Most common intents (placeholder - implement based on your intent tracking)
        most_common_intents = ['greeting', 'appointment_booking', 'symptom_inquiry']

        # Create or update analytics record
        analytics, created = ChatbotAnalytics.objects.update_or_create(
            date=target_date,
            defaults={
                'total_sessions': total_sessions,
                'total_messages': total_messages,
                'unique_users': unique_users,
                'resolved_queries': resolved_queries,
                'escalated_to_human': escalated_to_human,
                'average_session_duration': avg_duration,
                'most_common_intents': most_common_intents,
            }
        )

        action = 'Created' if created else 'Updated'
        self.stdout.write(
            self.style.SUCCESS(
                f'{action} analytics for {target_date}:\n'
                f'- Sessions: {total_sessions}\n'
                f'- Messages: {total_messages}\n'
                f'- Unique users: {unique_users}\n'
                f'- Resolved queries: {resolved_queries}\n'
                f'- Avg duration: {avg_duration}'
            )
        )