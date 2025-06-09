# Generated migration file
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Symptom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('category', models.CharField(choices=[('general', 'Triệu chứng chung'), ('respiratory', 'Hô hấp'), ('digestive', 'Tiêu hóa'), ('neurological', 'Thần kinh'), ('cardiovascular', 'Tim mạch'), ('musculoskeletal', 'Cơ xương khớp'), ('dermatological', 'Da liễu'), ('mental', 'Tâm thần')], default='general', max_length=50)),
                ('severity_weight', models.FloatField(default=1.0, help_text='Trọng số mức độ nghiêm trọng')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['category', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Disease',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField()),
                ('category', models.CharField(choices=[('infection', 'Nhiễm trùng'), ('chronic', 'Bệnh mãn tính'), ('acute', 'Bệnh cấp tính'), ('autoimmune', 'Tự miễn'), ('genetic', 'Di truyền'), ('lifestyle', 'Lối sống'), ('mental', 'Tâm thần')], max_length=50)),
                ('severity_level', models.CharField(choices=[('low', 'Nhẹ'), ('medium', 'Trung bình'), ('high', 'Nghiêm trọng'), ('critical', 'Nguy hiểm')], max_length=20)),
                ('treatment_advice', models.TextField(help_text='Lời khuyên điều trị cơ bản')),
                ('when_to_see_doctor', models.TextField(help_text='Khi nào cần đi khám bác sĩ')),
                ('prevention_tips', models.TextField(blank=True, help_text='Cách phòng ngừa')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='DiseaseSymptom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('probability', models.FloatField(help_text='Xác suất triệu chứng xuất hiện trong bệnh này (0.0-1.0)')),
                ('is_primary', models.BooleanField(default=False, help_text='Triệu chứng chính')),
                ('disease', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatbot.disease')),
                ('symptom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatbot.symptom')),
            ],
            options={
                'unique_together': {('disease', 'symptom')},
            },
        ),
        migrations.AddField(
            model_name='disease',
            name='symptoms',
            field=models.ManyToManyField(through='chatbot.DiseaseSymptom', to='chatbot.symptom'),
        ),
        migrations.CreateModel(
            name='DiseasePrediction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('predicted_diseases', models.JSONField(help_text='Danh sách bệnh được dự đoán với xác suất')),
                ('confidence_score', models.FloatField(help_text='Độ tin cậy của dự đoán')),
                ('user_feedback', models.CharField(blank=True, choices=[('helpful', 'Hữu ích'), ('somewhat', 'Tạm được'), ('not_helpful', 'Không hữu ích')], max_length=20, null=True)),
                ('doctor_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('selected_symptoms', models.ManyToManyField(to='chatbot.symptom')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='predictions', to='chatbot.chatsession')),
            ],
        ),
        migrations.CreateModel(
            name='PredictionFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accuracy_rating', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('actual_diagnosis', models.CharField(blank=True, max_length=200)),
                ('doctor_notes', models.TextField(blank=True)),
                ('suggested_improvements', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('prediction', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='detailed_feedback', to='chatbot.diseaseprediction')),
            ],
        ),
    ]