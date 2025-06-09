from django.contrib import admin
from .models import (
    ChatSession, ChatMessage, ChatbotKnowledge, ChatbotIntent, 
    ChatbotFeedback, ChatbotAnalytics,
    Symptom, Disease, DiseaseSymptom, DiseasePrediction, PredictionFeedback
)

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at', 'is_active', 'message_count')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'session_key')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Số tin nhắn'

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'sender', 'message_type', 'content_preview', 'created_at', 'is_read')
    list_filter = ('sender', 'message_type', 'is_read', 'created_at')
    search_fields = ('content', 'session__user__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Nội dung'

@admin.register(ChatbotKnowledge)
class ChatbotKnowledgeAdmin(admin.ModelAdmin):
    list_display = ('category', 'question_keywords_preview', 'answer_preview', 'priority', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'priority', 'created_at')
    search_fields = ('question_keywords', 'answer')
    list_editable = ('priority', 'is_active')
    ordering = ['-priority', '-created_at']
    
    def question_keywords_preview(self, obj):
        return obj.question_keywords[:50] + "..." if len(obj.question_keywords) > 50 else obj.question_keywords
    question_keywords_preview.short_description = 'Từ khóa'
    
    def answer_preview(self, obj):
        return obj.answer[:100] + "..." if len(obj.answer) > 100 else obj.answer
    answer_preview.short_description = 'Câu trả lời'

@admin.register(ChatbotIntent)
class ChatbotIntentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'action', 'is_active')
    list_filter = ('is_active', 'action')
    search_fields = ('name', 'description', 'action')
    list_editable = ('is_active',)

@admin.register(ChatbotFeedback)
class ChatbotFeedbackAdmin(admin.ModelAdmin):
    list_display = ('session', 'rating', 'comment_preview', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('comment', 'session__user__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def comment_preview(self, obj):
        return obj.comment[:100] + "..." if len(obj.comment) > 100 else obj.comment
    comment_preview.short_description = 'Bình luận'

@admin.register(ChatbotAnalytics)
class ChatbotAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_sessions', 'total_messages', 'unique_users', 'resolved_queries', 'escalated_to_human')
    list_filter = ('date',)
    date_hierarchy = 'date'
    readonly_fields = ('date', 'total_sessions', 'total_messages', 'unique_users', 'resolved_queries', 'escalated_to_human', 'average_session_duration')
    
    def has_add_permission(self, request):
        return False  # Analytics được tạo tự động
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'severity_weight', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'severity_weight', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('severity_weight', 'is_active')
    ordering = ['category', 'name']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'description', 'category')
        }),
        ('Cấu hình', {
            'fields': ('severity_weight', 'is_active')
        }),
    )

# Inline for DiseaseSymptom
class DiseaseSymptomInline(admin.TabularInline):
    model = DiseaseSymptom
    extra = 1
    fields = ('symptom', 'probability', 'is_primary')

@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'severity_level', 'symptom_count', 'is_active', 'created_at')
    list_filter = ('category', 'severity_level', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'treatment_advice')
    list_editable = ('is_active',)
    inlines = [DiseaseSymptomInline]
    
    fieldsets = (
        ('Thông tin bệnh', {
            'fields': ('name', 'description', 'category', 'severity_level')
        }),
        ('Thông tin y tế', {
            'fields': ('treatment_advice', 'when_to_see_doctor', 'prevention_tips')
        }),
        ('Cấu hình', {
            'fields': ('is_active',)
        }),
    )
    
    def symptom_count(self, obj):
        return obj.symptoms.count()
    symptom_count.short_description = 'Số triệu chứng'

@admin.register(DiseaseSymptom)
class DiseaseSymptomAdmin(admin.ModelAdmin):
    list_display = ('disease', 'symptom', 'probability', 'is_primary')
    list_filter = ('is_primary', 'probability', 'disease__category', 'symptom__category')
    search_fields = ('disease__name', 'symptom__name')
    list_editable = ('probability', 'is_primary')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('disease', 'symptom')

# Custom admin actions
@admin.action(description='Đánh dấu là đã được bác sĩ xác minh')
def mark_doctor_verified(modeladmin, request, queryset):
    queryset.update(doctor_verified=True)

@admin.action(description='Đánh dấu là chưa được bác sĩ xác minh')  
def mark_doctor_unverified(modeladmin, request, queryset):
    queryset.update(doctor_verified=False)

@admin.register(DiseasePrediction)
class DiseasePredictionAdmin(admin.ModelAdmin):
    list_display = ('session_user', 'symptom_list', 'top_prediction', 'confidence_score', 
                   'user_feedback', 'doctor_verified', 'created_at')
    list_filter = ('user_feedback', 'doctor_verified', 'confidence_score', 'created_at')
    search_fields = ('session__user__username', 'session__user__email')
    readonly_fields = ('session', 'selected_symptoms', 'predicted_diseases', 
                      'confidence_score', 'created_at')
    actions = [mark_doctor_verified, mark_doctor_unverified]
    
    def session_user(self, obj):
        return obj.session.user.get_full_name() if obj.session.user else "Anonymous"
    session_user.short_description = 'Người dùng'
    
    def symptom_list(self, obj):
        symptoms = obj.selected_symptoms.all()[:3]
        result = ', '.join([s.name for s in symptoms])
        if obj.selected_symptoms.count() > 3:
            result += f' (+{obj.selected_symptoms.count() - 3} khác)'
        return result
    symptom_list.short_description = 'Triệu chứng'
    
    def top_prediction(self, obj):
        if obj.predicted_diseases and len(obj.predicted_diseases) > 0:
            top = obj.predicted_diseases[0]
            return f"{top['disease']} ({top['probability']*100:.1f}%)"
        return "Không có"
    top_prediction.short_description = 'Dự đoán hàng đầu'

@admin.register(PredictionFeedback)
class PredictionFeedbackAdmin(admin.ModelAdmin):
    list_display = ('prediction_user', 'accuracy_rating', 'has_actual_diagnosis', 
                   'has_doctor_notes', 'created_at')
    list_filter = ('accuracy_rating', 'created_at')
    search_fields = ('prediction__session__user__username', 'actual_diagnosis', 'doctor_notes')
    readonly_fields = ('prediction', 'created_at')
    
    def prediction_user(self, obj):
        return obj.prediction.session.user.get_full_name() if obj.prediction.session.user else "Anonymous"
    prediction_user.short_description = 'Người dùng'
    
    def has_actual_diagnosis(self, obj):
        return bool(obj.actual_diagnosis)
    has_actual_diagnosis.boolean = True
    has_actual_diagnosis.short_description = 'Có chẩn đoán thực'
    
    def has_doctor_notes(self, obj):
        return bool(obj.doctor_notes)
    has_doctor_notes.boolean = True
    has_doctor_notes.short_description = 'Có ghi chú BS'