from django.contrib import admin
from .models import Question, Answer

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient', 'category', 'is_anonymous', 'created_at')
    list_filter = ('category', 'is_anonymous', 'created_at')
    search_fields = ('title', 'content', 'patient__user__username')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'doctor', 'is_helpful', 'created_at')
    list_filter = ('is_helpful', 'created_at')
    search_fields = ('question__title', 'doctor__user__username')