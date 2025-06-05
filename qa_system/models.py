from django.db import models
from django.contrib.auth import get_user_model
from doctors.models import Doctor
from patients.models import Patient

User = get_user_model()

class Question(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=50, blank=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    is_helpful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Answer by {self.doctor} for {self.question.title}"