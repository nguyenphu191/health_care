from django.core.management.base import BaseCommand
from chatbot.ml_models import DiseasePredictionModel

class Command(BaseCommand):
    help = 'Train disease prediction model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--retrain',
            action='store_true',
            help='Force retrain even if model exists',
        )

    def handle(self, *args, **options):
        self.stdout.write('Training disease prediction model...')
        
        model = DiseasePredictionModel()
        
        # Check if model already exists
        if not options['retrain'] and model.load_model():
            self.stdout.write(
                self.style.WARNING('Model already exists. Use --retrain to force retrain.')
            )
            
            # Show current accuracy
            accuracy = model.get_model_accuracy()
            self.stdout.write(f'Current model accuracy: {accuracy:.2%}')
            return
        
        # Train new model
        success = model.train_model()
        
        if success:
            accuracy = model.get_model_accuracy()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully trained model with accuracy: {accuracy:.2%}'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR('Failed to train model')
            )