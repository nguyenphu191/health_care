from django import forms
from .models import ChatbotFeedback, ChatMessage

class ChatMessageForm(forms.ModelForm):
    """Form để gửi tin nhắn chat"""
    content = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập tin nhắn của bạn...',
            'autocomplete': 'off'
        }),
        max_length=1000,
        label=''
    )
    
    class Meta:
        model = ChatMessage
        fields = ['content']

class ChatbotFeedbackForm(forms.ModelForm):
    """Form để đánh giá chatbot"""
    rating = forms.ChoiceField(
        choices=ChatbotFeedback.RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Đánh giá chatbot'
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Chia sẻ ý kiến của bạn về chatbot...'
        }),
        required=False,
        label='Ý kiến đóng góp'
    )
    
    class Meta:
        model = ChatbotFeedback
        fields = ['rating', 'comment']

class QuickAppointmentForm(forms.Form):
    """Form nhanh để đặt lịch từ chatbot"""
    doctor_specialty = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'VD: Tim mạch, Nhi khoa...'
        }),
        label='Chuyên khoa'
    )
    symptoms = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Mô tả triệu chứng của bạn...'
        }),
        label='Triệu chứng'
    )
    preferred_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='Ngày mong muốn'
    )
    urgent = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Cần khám gấp'
    )