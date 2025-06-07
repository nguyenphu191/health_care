from django.contrib import admin
from .models import ChatSession, ChatMessage, ChatbotKnowledge, ChatbotIntent, ChatbotFeedback, ChatbotAnalytics

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