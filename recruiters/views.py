from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Recruiter
from placement_team.models import RecruiterJobFair, Job_fairs
from students.models import RecruiterStudentAttendance, StudentRegistration
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


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
        
        # Get the recruiter's job fairs
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
        # ORDER BY timestamp DESC to show most recent first
        attendance_records = RecruiterStudentAttendance.objects.filter(
            recruiter_id=recruiter_id, 
            job_fair_id=selected_job_fair.job_fair_id
        ).order_by('-timestamp')
        
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
                    'student': student,
                    'status': record.status,
                    'round_1': record.round_1,
                    'round_2': record.round_2,
                    'round_3': record.round_3,
                    'notes': record.notes
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


@csrf_exempt
@require_POST
def update_student_status(request):
    if 'recruiter_id' not in request.session:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)
    
    recruiter_id = request.session['recruiter_id']
    job_fair_id = request.POST.get('job_fair_id')
    student_reg_number = request.POST.get('student_reg_number')
    new_status = request.POST.get('status')
    
    if not all([job_fair_id, student_reg_number, new_status]):
        return JsonResponse({'success': False, 'error': 'Missing required parameters'}, status=400)
    
    try:
        attendance = RecruiterStudentAttendance.objects.get(
            job_fair_id=job_fair_id,
            recruiter_id=recruiter_id,
            student_registration_number=student_reg_number
        )
        
        # Validate status value
        valid_statuses = [choice[0] for choice in RecruiterStudentAttendance.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': 'Invalid status value'}, status=400)
        
        attendance.status = new_status
        attendance.save()
        
        return JsonResponse({'success': True})
    
    except RecruiterStudentAttendance.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Attendance record not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def update_round_status(request):
    if 'recruiter_id' not in request.session:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)
    
    recruiter_id = request.session['recruiter_id']
    job_fair_id = request.POST.get('job_fair_id')
    student_reg_number = request.POST.get('student_reg_number')
    round_number = request.POST.get('round_number')  # Should be 'round_1', 'round_2', or 'round_3'
    new_status = request.POST.get('status')
    
    if not all([job_fair_id, student_reg_number, round_number, new_status]):
        return JsonResponse({'success': False, 'error': 'Missing required parameters'}, status=400)
    
    if round_number not in ['round_1', 'round_2', 'round_3']:
        return JsonResponse({'success': False, 'error': 'Invalid round number'}, status=400)
    
    try:
        attendance = RecruiterStudentAttendance.objects.get(
            job_fair_id=job_fair_id,
            recruiter_id=recruiter_id,
            student_registration_number=student_reg_number
        )
        
        # Validate status value
        valid_statuses = [choice[0] for choice in RecruiterStudentAttendance.ROUND_STATUS_CHOICES]
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': 'Invalid status value'}, status=400)
        
        # Update the appropriate round field
        setattr(attendance, round_number, new_status)
        attendance.save()
        
        return JsonResponse({'success': True})
    
    except RecruiterStudentAttendance.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Attendance record not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def update_student_notes(request):
    if 'recruiter_id' not in request.session:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)
    
    recruiter_id = request.session['recruiter_id']
    job_fair_id = request.POST.get('job_fair_id')
    student_reg_number = request.POST.get('student_reg_number')
    notes = request.POST.get('notes', '')
    
    if not all([job_fair_id, student_reg_number]):
        return JsonResponse({'success': False, 'error': 'Missing required parameters'}, status=400)
    
    try:
        attendance = RecruiterStudentAttendance.objects.get(
            job_fair_id=job_fair_id,
            recruiter_id=recruiter_id,
            student_registration_number=student_reg_number
        )
        
        attendance.notes = notes
        attendance.save()
        
        return JsonResponse({'success': True})
    
    except RecruiterStudentAttendance.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Attendance record not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



# Add this function to recruiters/views.py
import json

@csrf_exempt
@require_POST
def shortlist_multiple_students(request):
    if 'recruiter_id' not in request.session:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)
    
    recruiter_id = request.session['recruiter_id']
    job_fair_id = request.POST.get('job_fair_id')
    reg_numbers_json = request.POST.get('reg_numbers')
    
    if not job_fair_id or not reg_numbers_json:
        return JsonResponse({'success': False, 'error': 'Missing required parameters'}, status=400)
    
    try:
        # Parse JSON string to list
        reg_numbers = json.loads(reg_numbers_json)
        
        # Validate input
        if not isinstance(reg_numbers, list) or len(reg_numbers) == 0:
            return JsonResponse({'success': False, 'error': 'Invalid registration numbers'}, status=400)
        
        # Get all attendance records for these students
        from students.models import RecruiterStudentAttendance
        records_to_update = RecruiterStudentAttendance.objects.filter(
            job_fair_id=job_fair_id,
            recruiter_id=recruiter_id,
            student_registration_number__in=reg_numbers,
            status='pending'  # Only update those that are currently pending
        )
        
        # Update status to 'shortlisted'
        updated_count = records_to_update.update(status='shortlisted')
        
        return JsonResponse({
            'success': True, 
            'message': f'Successfully shortlisted {updated_count} students.',
            'updated_count': updated_count
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)