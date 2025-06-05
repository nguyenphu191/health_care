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

# New Profile Edit Forms
class DoctorProfileForm(forms.ModelForm):
    # User fields
    first_name = forms.CharField(label='Tên', max_length=150, required=True)
    last_name = forms.CharField(label='Họ', max_length=150, required=True)
    email = forms.EmailField(label='Email', required=True)
    phone_number = forms.CharField(label='Số điện thoại', max_length=15, required=False)
    date_of_birth = forms.DateField(
        label='Ngày sinh',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    address = forms.CharField(
        label='Địa chỉ',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )
    avatar = forms.ImageField(label='Ảnh đại diện', required=False)
    
    # Doctor fields
    specializations = forms.ModelMultipleChoiceField(
        label='Chuyên khoa',
        queryset=Specialization.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    experience_years = forms.IntegerField(label='Số năm kinh nghiệm', min_value=0, required=False)
    qualification = forms.CharField(
        label='Trình độ chuyên môn',
        widget=forms.Textarea(attrs={'rows': 4}),
        required=True
    )
    consultation_fee = forms.DecimalField(
        label='Phí tư vấn (VNĐ)',
        max_digits=10,
        decimal_places=2,
        required=False
    )
    bio = forms.CharField(
        label='Giới thiệu bản thân',
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'address', 'avatar']
    
    def __init__(self, *args, **kwargs):
        self.doctor_instance = kwargs.pop('doctor_instance', None)
        super().__init__(*args, **kwargs)
        
        if self.doctor_instance:
            self.fields['specializations'].initial = self.doctor_instance.specializations.all()
            self.fields['experience_years'].initial = self.doctor_instance.experience_years
            self.fields['qualification'].initial = self.doctor_instance.qualification
            self.fields['consultation_fee'].initial = self.doctor_instance.consultation_fee
            self.fields['bio'].initial = self.doctor_instance.bio
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        
        if self.doctor_instance and commit:
            # Update doctor fields
            self.doctor_instance.experience_years = self.cleaned_data.get('experience_years', 0)
            self.doctor_instance.qualification = self.cleaned_data['qualification']
            self.doctor_instance.consultation_fee = self.cleaned_data.get('consultation_fee', 0)
            self.doctor_instance.bio = self.cleaned_data.get('bio', '')
            self.doctor_instance.save()
            
            # Update specializations
            self.doctor_instance.specializations.set(self.cleaned_data['specializations'])
        
        return user

class PatientProfileForm(forms.ModelForm):
    # User fields
    first_name = forms.CharField(label='Tên', max_length=150, required=True)
    last_name = forms.CharField(label='Họ', max_length=150, required=True)
    email = forms.EmailField(label='Email', required=True)
    phone_number = forms.CharField(label='Số điện thoại', max_length=15, required=False)
    date_of_birth = forms.DateField(
        label='Ngày sinh',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    address = forms.CharField(
        label='Địa chỉ',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )
    avatar = forms.ImageField(label='Ảnh đại diện', required=False)
    
    # Patient fields
    gender = forms.ChoiceField(label='Giới tính', choices=Patient.GENDER_CHOICES, required=True)
    blood_type = forms.ChoiceField(
        label='Nhóm máu',
        choices=[('', 'Chọn nhóm máu')] + list(Patient.BLOOD_TYPE_CHOICES),
        required=False
    )
    emergency_contact = forms.CharField(
        label='Số điện thoại khẩn cấp',
        max_length=15,
        required=False
    )
    medical_history = forms.CharField(
        label='Tiền sử bệnh',
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False
    )
    allergies = forms.CharField(
        label='Dị ứng',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )
    current_medications = forms.CharField(
        label='Thuốc đang sử dụng',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'address', 'avatar']
    
    def __init__(self, *args, **kwargs):
        self.patient_instance = kwargs.pop('patient_instance', None)
        super().__init__(*args, **kwargs)
        
        if self.patient_instance:
            self.fields['gender'].initial = self.patient_instance.gender
            self.fields['blood_type'].initial = self.patient_instance.blood_type
            self.fields['emergency_contact'].initial = self.patient_instance.emergency_contact
            self.fields['medical_history'].initial = self.patient_instance.medical_history
            self.fields['allergies'].initial = self.patient_instance.allergies
            self.fields['current_medications'].initial = self.patient_instance.current_medications
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        
        if self.patient_instance and commit:
            # Update patient fields
            self.patient_instance.gender = self.cleaned_data['gender']
            self.patient_instance.blood_type = self.cleaned_data.get('blood_type', '')
            self.patient_instance.emergency_contact = self.cleaned_data.get('emergency_contact', '')
            self.patient_instance.medical_history = self.cleaned_data.get('medical_history', '')
            self.patient_instance.allergies = self.cleaned_data.get('allergies', '')
            self.patient_instance.current_medications = self.cleaned_data.get('current_medications', '')
            self.patient_instance.save()
        
        return user