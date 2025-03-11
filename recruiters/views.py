from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Recruiter
from placement_team.models import RecruiterJobFair, Job_fairs
from students.models import RecruiterStudentAttendance, StudentRegistration
from django.http import JsonResponse

def recruiter_login(request):
    if 'recruiter_id' in request.session:
        # If recruiter is already logged in, redirect to dashboard
        return redirect('recruiter_dashboard')
        
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            recruiter = Recruiter.objects.get(recruiter_email=email, recruiter_password=password)
            # Store recruiter ID in session
            request.session['recruiter_id'] = recruiter.recruiter_id
            request.session['recruiter_email'] = recruiter.recruiter_email
            return redirect('recruiter_dashboard')
        except Recruiter.DoesNotExist:
            messages.error(request, "Invalid email or password")
    
    return render(request, 'recruiters_app/login.html')

def recruiter_dashboard(request):
    if 'recruiter_id' not in request.session:
        # If recruiter is not logged in, redirect to login page
        return redirect('recruiter_login')
    
    recruiter_id = request.session['recruiter_id']
    recruiter_email = request.session['recruiter_email']
    
    try:
        recruiter = Recruiter.objects.get(recruiter_id=recruiter_id)
        
        # Get only the job fairs this recruiter has attended through RecruiterJobFair
        recruiter_job_fairs = RecruiterJobFair.objects.filter(recruiter=recruiter)
        
        # If no job fairs found, render with empty data
        if not recruiter_job_fairs.exists():
            return render(request, 'recruiters_app/dashboard.html', {
                'recruiter_email': recruiter_email,
                'recruiter_id': recruiter_id,
                'job_fairs': [],
                'selected_job_fair': None,
                'qr_code_url': None,
                'attendances': []
            })
        
        # Get the selected job fair (from query parameter or default to the first one)
        selected_job_fair_id = request.GET.get('job_fair_id')
        
        # If job_fair_id provided in URL, validate and use it, otherwise use the first job fair
        selected_job_fair = None
        selected_rjf = None
        if selected_job_fair_id:
            # Find the selected job fair from the recruiter's job fairs
            for rjf in recruiter_job_fairs:
                if str(rjf.job_fair.job_fair_id) == selected_job_fair_id:
                    selected_job_fair = rjf.job_fair
                    selected_rjf = rjf
                    break
        
        # If no valid job_fair_id was provided or found, use the first one
        if not selected_job_fair:
            selected_rjf = recruiter_job_fairs.first()
            selected_job_fair = selected_rjf.job_fair
        
        # Get QR code URL for the selected job fair
        qr_code_url = selected_rjf.qr_code.url if selected_rjf.qr_code else None
        
        # Get student attendances for this recruiter at the selected job fair
        attendance_records = RecruiterStudentAttendance.objects.filter(
            recruiter_id=recruiter_id, 
            job_fair_id=selected_job_fair.job_fair_id
        )
        
        # Enhance attendance records with student details
        attendances = []
        for record in attendance_records:
            try:
                student = StudentRegistration.objects.get(
                    registration_number=record.student_registration_number,
                    job_fair_id=selected_job_fair.job_fair_id
                )
                attendances.append({
                    'timestamp': record.timestamp,
                    'student': student
                })
            except StudentRegistration.DoesNotExist:
                # Handle case where student record not found
                pass
        
        # Prepare a list of job fairs this recruiter has attended for the dropdown
        job_fairs = []
        for rjf in recruiter_job_fairs:
            job_fairs.append({
                'id': rjf.job_fair.job_fair_id,
                'district': rjf.job_fair.district,
                'date': rjf.job_fair.date_of_job_fair,
                'qr_code_url': rjf.qr_code.url if rjf.qr_code else None
            })
        
        return render(request, 'recruiters_app/dashboard.html', {
            'recruiter_email': recruiter_email,
            'recruiter_id': recruiter_id,
            'job_fairs': job_fairs,
            'selected_job_fair': selected_job_fair,
            'qr_code_url': qr_code_url,
            'attendances': attendances
        })
        
    except Recruiter.DoesNotExist:
        # Handle invalid session data
        del request.session['recruiter_id']
        del request.session['recruiter_email']
        return redirect('recruiter_login')

def recruiter_logout(request):
    # Clear session data
    if 'recruiter_id' in request.session:
        del request.session['recruiter_id']
    if 'recruiter_email' in request.session:
        del request.session['recruiter_email']
    return redirect('recruiter_login')

# Add a new view to fetch attendances for a specific job fair
def get_job_fair_attendances(request, job_fair_id):
    if 'recruiter_id' not in request.session:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    recruiter_id = request.session['recruiter_id']
    
    # Get all attendance records for this job fair and recruiter
    attendance_records = RecruiterStudentAttendance.objects.filter(
        recruiter_id=recruiter_id,
        job_fair_id=job_fair_id
    )
    
    # Prepare the response data
    attendances_data = []
    for record in attendance_records:
        try:
            student = StudentRegistration.objects.get(
                registration_number=record.student_registration_number,
                job_fair_id=job_fair_id
            )
            
            attendances_data.append({
                'registration_number': student.registration_number,
                'name': student.name,
                'college_name': student.college_name,
                'has_resume': bool(student.resume),
                'resume_url': student.resume.url if student.resume else None,
                'timestamp': record.timestamp.strftime("%b %d, %Y, %I:%M %p")
            })
        except StudentRegistration.DoesNotExist:
            # Skip if student record not found
            pass
    
    return JsonResponse({'attendances': attendances_data})