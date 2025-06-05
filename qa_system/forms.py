from django import forms
from .models import Question, Answer

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'content', 'category', 'is_anonymous']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
            'title': forms.TextInput(attrs={'placeholder': 'Nhập tiêu đề câu hỏi'})
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Nhập câu trả lời...'})
        }