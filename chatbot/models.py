from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class ChatSession(models.Model):
    """Phiên chat của người dùng"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions', null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)  # Cho anonymous users
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        user_display = self.user.username if self.user else f"Anonymous-{self.session_key}"
        return f"Chat Session - {user_display} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"

class ChatMessage(models.Model):
    """Tin nhắn trong cuộc hội thoại"""
    SENDER_CHOICES = (
        ('user', 'Người dùng'),
        ('bot', 'Chatbot'),
        ('system', 'Hệ thống'),
    )
    
    MESSAGE_TYPE_CHOICES = (
        ('text', 'Văn bản'),
        ('quick_reply', 'Trả lời nhanh'),
        ('card', 'Card'),
        ('appointment_booking', 'Đặt lịch hẹn'),
        ('doctor_list', 'Danh sách bác sĩ'),
        ('disease_prediction', 'Dự đoán bệnh'),
        ('disease_prediction_result', 'Kết quả dự đoán bệnh'),
    )
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message_type = models.CharField(max_length=30, choices=MESSAGE_TYPE_CHOICES, default='text')
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)  # Lưu thêm thông tin (buttons, cards, etc.)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.get_sender_display()}: {self.content[:50]}..."

class ChatbotKnowledge(models.Model):
    """Kiến thức của chatbot"""
    CATEGORY_CHOICES = (
        ('faq', 'Câu hỏi thường gặp'),
        ('medical', 'Y tế'),
        ('appointment', 'Đặt lịch hẹn'),
        ('system', 'Hệ thống'),
        ('emergency', 'Cấp cứu'),
    )
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    question_keywords = models.TextField(help_text="Các từ khóa để nhận diện câu hỏi, cách nhau bằng dấu phẩy")
    answer = models.TextField()
    follow_up_questions = models.JSONField(default=list, blank=True)  # Câu hỏi gợi ý tiếp theo
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)  # Độ ưu tiên khi có nhiều câu trả lời phù hợp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return f"{self.get_category_display()}: {self.question_keywords[:50]}..."

class ChatbotIntent(models.Model):
    """Ý định của người dùng"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    training_phrases = models.JSONField(default=list)  # Các cụm từ để train
    action = models.CharField(max_length=100)  # Hành động tương ứng
    parameters = models.JSONField(default=dict, blank=True)  # Tham số cần thiết
    response_templates = models.JSONField(default=list)  # Template phản hồi
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class ChatbotFeedback(models.Model):
    """Phản hồi từ người dùng về chatbot"""
    RATING_CHOICES = (
        (1, 'Rất không hài lòng'),
        (2, 'Không hài lòng'),
        (3, 'Bình thường'),
        (4, 'Hài lòng'),
        (5, 'Rất hài lòng'),
    )
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='feedbacks')
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback: {self.rating}/5 - {self.comment[:50]}..."

class ChatbotAnalytics(models.Model):
    """Thống kê sử dụng chatbot"""
    date = models.DateField()
    total_sessions = models.IntegerField(default=0)
    total_messages = models.IntegerField(default=0)
    unique_users = models.IntegerField(default=0)
    resolved_queries = models.IntegerField(default=0)
    escalated_to_human = models.IntegerField(default=0)
    average_session_duration = models.DurationField(null=True, blank=True)
    most_common_intents = models.JSONField(default=list, blank=True)
    
    class Meta:
        unique_together = ['date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics for {self.date}"

# Disease Prediction Models

class Symptom(models.Model):
    """Model lưu trữ triệu chứng"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=[
        ('general', 'Triệu chứng chung'),
        ('respiratory', 'Hô hấp'),
        ('digestive', 'Tiêu hóa'),
        ('neurological', 'Thần kinh'),
        ('cardiovascular', 'Tim mạch'),
        ('musculoskeletal', 'Cơ xương khớp'),
        ('dermatological', 'Da liễu'),
        ('mental', 'Tâm thần'),
    ], default='general')
    severity_weight = models.FloatField(default=1.0, help_text="Trọng số mức độ nghiêm trọng")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return self.name

class Disease(models.Model):
    """Model lưu trữ bệnh"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=[
        ('infection', 'Nhiễm trùng'),
        ('chronic', 'Bệnh mãn tính'),
        ('acute', 'Bệnh cấp tính'),
        ('autoimmune', 'Tự miễn'),
        ('genetic', 'Di truyền'),
        ('lifestyle', 'Lối sống'),
        ('mental', 'Tâm thần'),
    ])
    severity_level = models.CharField(max_length=20, choices=[
        ('low', 'Nhẹ'),
        ('medium', 'Trung bình'),
        ('high', 'Nghiêm trọng'),
        ('critical', 'Nguy hiểm'),
    ])
    symptoms = models.ManyToManyField(Symptom, through='DiseaseSymptom')
    treatment_advice = models.TextField(help_text="Lời khuyên điều trị cơ bản")
    when_to_see_doctor = models.TextField(help_text="Khi nào cần đi khám bác sĩ")
    prevention_tips = models.TextField(blank=True, help_text="Cách phòng ngừa")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class DiseaseSymptom(models.Model):
    """Model trung gian lưu trữ mối quan hệ bệnh-triệu chứng"""
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    probability = models.FloatField(
        help_text="Xác suất triệu chứng xuất hiện trong bệnh này (0.0-1.0)"
    )
    is_primary = models.BooleanField(default=False, help_text="Triệu chứng chính")
    
    class Meta:
        unique_together = ['disease', 'symptom']
    
    def __str__(self):
        return f"{self.disease.name} - {self.symptom.name} ({self.probability})"

class DiseasePrediction(models.Model):
    """Model lưu trữ kết quả dự đoán bệnh"""
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='predictions')
    selected_symptoms = models.ManyToManyField(Symptom)
    predicted_diseases = models.JSONField(help_text="Danh sách bệnh được dự đoán với xác suất")
    confidence_score = models.FloatField(help_text="Độ tin cậy của dự đoán")
    user_feedback = models.CharField(max_length=20, choices=[
        ('helpful', 'Hữu ích'),
        ('somewhat', 'Tạm được'),
        ('not_helpful', 'Không hữu ích'),
    ], null=True, blank=True)
    doctor_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Prediction for {self.session} - {self.created_at}"

class PredictionFeedback(models.Model):
    """Model lưu feedback chi tiết về dự đoán"""
    prediction = models.OneToOneField(DiseasePrediction, on_delete=models.CASCADE, related_name='detailed_feedback')
    accuracy_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    actual_diagnosis = models.CharField(max_length=200, blank=True)
    doctor_notes = models.TextField(blank=True)
    suggested_improvements = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback for {self.prediction}"