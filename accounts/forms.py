from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from doctors.models import Doctor, Specialization
from patients.models import Patient

User = get_user_model()

class DoctorRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = forms.CharField(required=True)
    license_number = forms.CharField(required=True)
    specializations = forms.ModelMultipleChoiceField(
        queryset=Specialization.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    qualification = forms.CharField(widget=forms.Textarea)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 
                 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'doctor'
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        
        if commit:
            user.save()
            doctor = Doctor.objects.create(
                user=user,
                license_number=self.cleaned_data['license_number'],
                qualification=self.cleaned_data['qualification']
            )
            doctor.specializations.set(self.cleaned_data['specializations'])
        
        return user

class PatientRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = forms.CharField(required=True)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=Patient.GENDER_CHOICES)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number',
                 'date_of_birth', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'patient'
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        user.date_of_birth = self.cleaned_data['date_of_birth']
        
        if commit:
            user.save()
            Patient.objects.create(
                user=user,
                gender=self.cleaned_data['gender']
            )
        
        return user