import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
from django.conf import settings
from .models import Disease, Symptom, DiseaseSymptom, DiseasePrediction
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class DiseasePredictionModel:
    """Machine Learning model để dự đoán bệnh"""
    
    def __init__(self):
        self.model = None
        self.symptoms_list = []
        self.diseases_list = []
        
        # Tạo thư mục ml_models nếu chưa có
        self.model_dir = os.path.join(settings.BASE_DIR, 'ml_models')
        os.makedirs(self.model_dir, exist_ok=True)
        
        self.model_path = os.path.join(self.model_dir, 'disease_prediction.pkl')
        self.symptoms_path = os.path.join(self.model_dir, 'symptoms_mapping.pkl')
        self.diseases_path = os.path.join(self.model_dir, 'diseases_mapping.pkl')
        
    def prepare_training_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """Chuẩn bị dữ liệu training từ database"""
        try:
            print("Preparing training data...")
            
            # Lấy tất cả symptoms và diseases
            symptoms = list(Symptom.objects.filter(is_active=True).values_list('name', flat=True))
            diseases = list(Disease.objects.filter(is_active=True).values_list('name', flat=True))
            
            print(f"Found {len(symptoms)} symptoms and {len(diseases)} diseases")
            
            if not symptoms or not diseases:
                print("ERROR: No symptoms or diseases found in database")
                return pd.DataFrame(), pd.Series()
            
            self.symptoms_list = symptoms
            self.diseases_list = diseases
            
            # Tạo training data
            training_data = []
            
            for disease in Disease.objects.filter(is_active=True):
                # Lấy triệu chứng của bệnh này
                disease_symptoms = DiseaseSymptom.objects.filter(disease=disease)
                
                print(f"Processing disease: {disease.name} with {disease_symptoms.count()} symptoms")
                
                if disease_symptoms.count() == 0:
                    print(f"WARNING: Disease {disease.name} has no symptoms")
                    continue
                
                # Tạo vector triệu chứng (0/1 cho mỗi triệu chứng)
                symptom_vector = [0.0] * len(symptoms)
                
                for ds in disease_symptoms:
                    if ds.symptom.name in symptoms:
                        idx = symptoms.index(ds.symptom.name)
                        # Sử dụng probability làm weight
                        symptom_vector[idx] = ds.probability
                
                training_data.append({
                    'symptoms': symptom_vector,
                    'disease': disease.name
                })
            
            print(f"Created {len(training_data)} training samples")
            
            if not training_data:
                print("ERROR: No training data created")
                return pd.DataFrame(), pd.Series()
            
            # Chuyển đổi thành DataFrame
            X_data = []
            y_data = []
            
            for data in training_data:
                X_data.append(data['symptoms'])
                y_data.append(data['disease'])
            
            X = pd.DataFrame(X_data, columns=symptoms)
            y = pd.Series(y_data)
            
            print(f"Training data shape: X={X.shape}, y={y.shape}")
            print(f"Unique diseases: {y.nunique()}")
            
            return X, y
            
        except Exception as e:
            print(f"ERROR in prepare_training_data: {e}")
            logger.error(f"Error preparing training data: {e}")
            return pd.DataFrame(), pd.Series()
    
    def train_model(self) -> bool:
        """Train model với dữ liệu từ database"""
        try:
            print("Starting model training...")
            
            X, y = self.prepare_training_data()
            
            if X.empty or y.empty:
                print("ERROR: No training data available")
                logger.error("No training data available")
                return False
            
            # Kiểm tra nếu chỉ có 1 class
            if y.nunique() < 2:
                print("ERROR: Need at least 2 different diseases to train model")
                logger.error("Need at least 2 different diseases to train model")
                return False
            
            # Split data - sử dụng stratify nếu có đủ samples
            try:
                if len(y) >= 10:  # Enough data for splitting
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y, test_size=0.2, random_state=42, stratify=y
                    )
                else:
                    # Not enough data for splitting, use all data for training
                    X_train, X_test, y_train, y_test = X, X, y, y
                    print("WARNING: Using all data for training due to small dataset")
                    
            except ValueError as e:
                print(f"WARNING: Cannot stratify split, using random split: {e}")
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
            
            print(f"Training set: {X_train.shape}, Test set: {X_test.shape}")
            
            # Train Random Forest model với parameters tối ưu cho dataset nhỏ
            self.model = RandomForestClassifier(
                n_estimators=50,  # Giảm xuống để tránh overfitting
                max_depth=5,      # Giảm depth
                min_samples_split=2,
                min_samples_leaf=1,
                random_state=42,
                class_weight='balanced'  # Giải quyết imbalanced data
            )
            
            print("Training RandomForest model...")
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            print(f"Model trained successfully with accuracy: {accuracy:.2f}")
            logger.info(f"Model trained with accuracy: {accuracy:.2f}")
            
            # Save model
            self.save_model()
            
            return True
            
        except Exception as e:
            print(f"ERROR in train_model: {e}")
            logger.error(f"Error training model: {e}")
            return False
    
    def save_model(self):
        """Lưu model và mapping"""
        try:
            print("Saving model...")
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.symptoms_list, self.symptoms_path)
            joblib.dump(self.diseases_list, self.diseases_path)
            print(f"Model saved to {self.model_path}")
            logger.info("Model saved successfully")
        except Exception as e:
            print(f"ERROR saving model: {e}")
            logger.error(f"Error saving model: {e}")
    
    def load_model(self) -> bool:
        """Load model đã train"""
        try:
            if (os.path.exists(self.model_path) and 
                os.path.exists(self.symptoms_path) and 
                os.path.exists(self.diseases_path)):
                
                self.model = joblib.load(self.model_path)
                self.symptoms_list = joblib.load(self.symptoms_path)
                self.diseases_list = joblib.load(self.diseases_path)
                
                print("Model loaded successfully")
                logger.info("Model loaded successfully")
                return True
            else:
                print("Model files not found")
                logger.warning("Model files not found")
                return False
        except Exception as e:
            print(f"ERROR loading model: {e}")
            logger.error(f"Error loading model: {e}")
            return False
    
    def predict_disease(self, selected_symptoms: List[str]) -> List[Dict]:
        """Dự đoán bệnh dựa trên triệu chứng"""
        try:
            print(f"Predicting disease for symptoms: {selected_symptoms}")
            
            if not self.model:
                print("No model found, attempting to load...")
                if not self.load_model():
                    print("No model found, training new model...")
                    if not self.train_model():
                        print("ERROR: Failed to train model")
                        return []
            
            # Tạo vector triệu chứng
            symptom_vector = [0.0] * len(self.symptoms_list)
            
            for symptom in selected_symptoms:
                if symptom in self.symptoms_list:
                    idx = self.symptoms_list.index(symptom)
                    symptom_vector[idx] = 1.0
                else:
                    print(f"WARNING: Symptom '{symptom}' not in training data")
            
            # Kiểm tra nếu không có triệu chứng nào được recognize
            if sum(symptom_vector) == 0:
                print("ERROR: No recognized symptoms")
                return []
            
            # Reshape để predict
            X_predict = np.array(symptom_vector).reshape(1, -1)
            
            # Dự đoán xác suất cho tất cả các bệnh
            probabilities = self.model.predict_proba(X_predict)[0]
            classes = self.model.classes_
            
            print(f"Model predicted {len(probabilities)} probabilities")
            
            # Tạo danh sách kết quả
            predictions = []
            for i, disease in enumerate(classes):
                if probabilities[i] > 0.05:  # Threshold thấp hơn để có nhiều kết quả hơn
                    confidence = 'high' if probabilities[i] > 0.6 else 'medium' if probabilities[i] > 0.3 else 'low'
                    predictions.append({
                        'disease': disease,
                        'probability': float(probabilities[i]),
                        'confidence': confidence
                    })
            
            # Sắp xếp theo xác suất giảm dần
            predictions.sort(key=lambda x: x['probability'], reverse=True)
            
            print(f"Returning {len(predictions)} predictions")
            return predictions[:5]  # Trả về top 5 bệnh có khả năng nhất
            
        except Exception as e:
            print(f"ERROR in predict_disease: {e}")
            logger.error(f"Error predicting disease: {e}")
            return []
    
    def get_disease_info(self, disease_name: str) -> Dict:
        """Lấy thông tin chi tiết về bệnh"""
        try:
            disease = Disease.objects.get(name=disease_name, is_active=True)
            return {
                'name': disease.name,
                'description': disease.description,
                'category': disease.get_category_display(),
                'severity': disease.get_severity_level_display(),
                'treatment_advice': disease.treatment_advice,
                'when_to_see_doctor': disease.when_to_see_doctor,
                'prevention_tips': disease.prevention_tips,
            }
        except Disease.DoesNotExist:
            return {}
        except Exception as e:
            logger.error(f"Error getting disease info: {e}")
            return {}
    
    def get_model_accuracy(self) -> float:
        """Tính accuracy của model hiện tại"""
        try:
            if not self.model:
                return 0.0
                
            X, y = self.prepare_training_data()
            if X.empty:
                return 0.0
                
            y_pred = self.model.predict(X)
            return accuracy_score(y, y_pred)
        except Exception as e:
            logger.error(f"Error calculating accuracy: {e}")
            return 0.0

class DiseasePredictor:
    """Wrapper service cho disease prediction"""
    
    def __init__(self):
        self.ml_model = DiseasePredictionModel()
    
    def predict_from_symptoms(self, session, selected_symptoms: List[str]) -> Dict:
        """Dự đoán bệnh và lưu kết quả"""
        try:
            print(f"DiseasePredictor: Processing symptoms {selected_symptoms}")
            
            # Dự đoán bằng ML model
            predictions = self.ml_model.predict_disease(selected_symptoms)
            
            if not predictions:
                return {
                    'success': False,
                    'message': 'Không thể dự đoán bệnh với các triệu chứng đã chọn. Vui lòng thử chọn thêm triệu chứng khác hoặc đặt lịch khám với bác sĩ.'
                }
            
            # Tính confidence score
            confidence_score = predictions[0]['probability'] if predictions else 0.0
            
            # Lưu kết quả dự đoán
            prediction = DiseasePrediction.objects.create(
                session=session,
                predicted_diseases=predictions,
                confidence_score=confidence_score
            )
            
            # Thêm triệu chứng đã chọn
            symptoms = Symptom.objects.filter(name__in=selected_symptoms)
            prediction.selected_symptoms.set(symptoms)
            
            print(f"Saved prediction with ID: {prediction.id}")
            
            # Tạo response
            response = {
                'success': True,
                'prediction_id': prediction.id,
                'predictions': predictions,
                'confidence_score': confidence_score,
                'message': self._format_prediction_message(predictions, confidence_score)
            }
            
            return response
            
        except Exception as e:
            print(f"ERROR in predict_from_symptoms: {e}")
            logger.error(f"Error in disease prediction: {e}")
            return {
                'success': False,
                'message': 'Có lỗi xảy ra trong quá trình dự đoán. Vui lòng thử lại sau.'
            }
    
    def _format_prediction_message(self, predictions: List[Dict], confidence: float) -> str:
        """Format tin nhắn kết quả dự đoán"""
        if not predictions:
            return "Không thể xác định bệnh cụ thể với các triệu chứng này."
        
        message = "🔍 **Kết quả dự đoán:**\n\n"
        
        for i, pred in enumerate(predictions[:3], 1):
            disease_info = self.ml_model.get_disease_info(pred['disease'])
            probability_percent = pred['probability'] * 100
            
            message += f"**{i}. {pred['disease']}** ({probability_percent:.1f}%)\n"
            
            if disease_info:
                message += f"📝 {disease_info['description'][:100]}...\n"
                message += f"⚠️ Mức độ: {disease_info['severity']}\n\n"
        
        # Thêm lời khuyên
        if confidence > 0.6:
            message += "✅ **Độ tin cậy: Cao**\n"
        elif confidence > 0.3:
            message += "⚡ **Độ tin cậy: Trung bình**\n"
        else:
            message += "⚠️ **Độ tin cậy: Thấp**\n"
        
        message += "\n⚠️ **Lưu ý quan trọng:**\n"
        message += "• Đây chỉ là dự đoán hỗ trợ, không thay thế chẩn đoán của bác sĩ\n"
        message += "• Vui lòng đặt lịch khám để được chẩn đoán chính xác\n"
        message += "• Nếu triệu chứng nghiêm trọng, hãy đến bệnh viện ngay"
        
        return message
    
    def get_available_symptoms(self) -> Dict:
        """Lấy danh sách triệu chứng có sẵn"""
        try:
            symptoms = Symptom.objects.filter(is_active=True).order_by('category', 'name')
            
            result = {}
            for symptom in symptoms:
                category = symptom.get_category_display()
                if category not in result:
                    result[category] = []
                
                result[category].append({
                    'id': symptom.id,
                    'name': symptom.name,
                    'description': symptom.description
                })
            
            return result
        except Exception as e:
            logger.error(f"Error getting available symptoms: {e}")
            return {}