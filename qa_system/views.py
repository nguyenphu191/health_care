from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Question, Answer
from .forms import QuestionForm, AnswerForm
from patients.models import Patient

@login_required
def qa_list(request):
    questions = Question.objects.all()
    return render(request, 'qa_system/qa_list.html', {'questions': questions})

@login_required
def ask_question(request):
    if request.user.user_type != 'patient':
        return redirect('home')
    
    patient = get_object_or_404(Patient, user=request.user)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.patient = patient
            question.save()
            messages.success(request, 'Đặt câu hỏi thành công!')
            return redirect('qa_list')
    else:
        form = QuestionForm()
    
    return render(request, 'qa_system/ask_question.html', {'form': form})

@login_required
def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    answers = Answer.objects.filter(question=question)
    
    return render(request, 'qa_system/question_detail.html', {
        'question': question,
        'answers': answers
    })