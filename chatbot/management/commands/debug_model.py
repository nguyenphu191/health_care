from django.core.management.base import BaseCommand
from chatbot.models import Disease, Symptom, DiseaseSymptom
from chatbot.ml_models import DiseasePredictionModel

class Command(BaseCommand):
    help = 'Debug disease prediction model training'

    def handle(self, *args, **options):
        self.stdout.write('=== Disease Prediction Model Debug ===')
        
        # Check database data
        self.stdout.write('\n1. Checking database data...')
        
        symptoms_count = Symptom.objects.filter(is_active=True).count()
        diseases_count = Disease.objects.filter(is_active=True).count()
        relations_count = DiseaseSymptom.objects.count()
        
        self.stdout.write(f'   Symptoms: {symptoms_count}')
        self.stdout.write(f'   Diseases: {diseases_count}')
        self.stdout.write(f'   Disease-Symptom relations: {relations_count}')
        
        if symptoms_count == 0:
            self.stdout.write(self.style.ERROR('   ERROR: No symptoms found!'))
            return
            
        if diseases_count == 0:
            self.stdout.write(self.style.ERROR('   ERROR: No diseases found!'))
            return
            
        if relations_count == 0:
            self.stdout.write(self.style.ERROR('   ERROR: No disease-symptom relations found!'))
            return
        
        # Check each disease has symptoms
        self.stdout.write('\n2. Checking disease-symptom relationships...')
        for disease in Disease.objects.filter(is_active=True):
            symptom_count = disease.symptoms.count()
            self.stdout.write(f'   {disease.name}: {symptom_count} symptoms')
            if symptom_count == 0:
                self.stdout.write(self.style.WARNING(f'      WARNING: {disease.name} has no symptoms!'))
        
        # Test model training
        self.stdout.write('\n3. Testing model training...')
        
        try:
            model = DiseasePredictionModel()
            
            # Test data preparation
            self.stdout.write('   Preparing training data...')
            X, y = model.prepare_training_data()
            
            if X.empty or y.empty:
                self.stdout.write(self.style.ERROR('   ERROR: Failed to prepare training data'))
                return
            
            self.stdout.write(f'   Training data shape: X={X.shape}, y={y.shape}')
            self.stdout.write(f'   Unique diseases: {y.nunique()}')
            
            # Test model training
            self.stdout.write('   Training model...')
            success = model.train_model()
            
            if success:
                self.stdout.write(self.style.SUCCESS('   Model training completed successfully!'))
                
                # Test prediction
                self.stdout.write('\n4. Testing prediction...')
                test_symptoms = ['Sốt', 'Đau đầu', 'Ho']
                predictions = model.predict_disease(test_symptoms)
                
                if predictions:
                    self.stdout.write(f'   Test prediction successful! Found {len(predictions)} predictions:')
                    for pred in predictions:
                        self.stdout.write(f'      {pred["disease"]}: {pred["probability"]*100:.1f}%')
                else:
                    self.stdout.write(self.style.WARNING('   WARNING: No predictions returned'))
                    
            else:
                self.stdout.write(self.style.ERROR('   ERROR: Model training failed'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ERROR: {str(e)}'))
            import traceback
            self.stdout.write(traceback.format_exc())
        
        self.stdout.write('\n=== Debug Complete ===')