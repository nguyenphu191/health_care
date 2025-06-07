from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from chatbot.models import ChatSession, ChatMessage

class Command(BaseCommand):
    help = 'Clean up old chat sessions and messages'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to keep chat data (default: 30)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        days_to_keep = options['days']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        
        self.stdout.write(f'Cleaning up chat data older than {days_to_keep} days...')
        self.stdout.write(f'Cutoff date: {cutoff_date}')
        
        # Find old sessions
        old_sessions = ChatSession.objects.filter(
            created_at__lt=cutoff_date,
            is_active=False  # Only delete inactive sessions
        )
        
        # Find old messages
        old_messages = ChatMessage.objects.filter(
            created_at__lt=cutoff_date
        )
        
        session_count = old_sessions.count()
        message_count = old_messages.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN - Would delete:\n'
                    f'- {session_count} chat sessions\n'
                    f'- {message_count} chat messages'
                )
            )
        else:
            if session_count > 0 or message_count > 0:
                confirm = input(
                    f'This will permanently delete {session_count} sessions and {message_count} messages. '
                    f'Are you sure? (yes/no): '
                )
                
                if confirm.lower() == 'yes':
                    # Delete messages first (due to foreign key constraints)
                    deleted_messages = old_messages.delete()
                    deleted_sessions = old_sessions.delete()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully deleted:\n'
                            f'- {deleted_sessions[0]} chat sessions\n'
                            f'- {deleted_messages[0]} chat messages'
                        )
                    )
                else:
                    self.stdout.write('Cleanup cancelled.')
            else:
                self.stdout.write('No old data found to clean up.')
        
        # Show current statistics
        current_sessions = ChatSession.objects.count()
        current_messages = ChatMessage.objects.count()
        
        self.stdout.write(
            f'\nCurrent data:\n'
            f'- {current_sessions} chat sessions\n'
            f'- {current_messages} chat messages'
        )