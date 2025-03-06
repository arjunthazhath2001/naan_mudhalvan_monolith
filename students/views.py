from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import StudentRegistrationForm
from .models import StudentRegistration

def register_for_job_fair(request, job_fair_id):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Create but don't save the form instance yet
            student_registration = form.save(commit=False)
            # Add the job_fair_id
            student_registration.job_fair_id = job_fair_id
            # Now save the instance
            student_registration.save()
            messages.success(request, 'Registration successful! Thank you for registering for the job fair.')
            return redirect('registration_success')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'students_app/registration_form.html', {
        'form': form,
        'job_fair_id': job_fair_id
    })

def registration_success(request):
    return render(request, 'students_app/registration_success.html')