from django.db import models

class StudentRegistration(models.Model):
    job_fair_id = models.IntegerField()
    name = models.CharField(max_length=100)
    college_name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=50)
    email = models.EmailField()
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    registration_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'student_registrations'
        
    def __str__(self):
        return f"{self.name} - {self.college_name}"


class RecruiterStudentAttendance(models.Model):
    job_fair_id = models.IntegerField()
    recruiter_id = models.IntegerField()
    student_registration_number = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'job_fair_recruiter_student_attendance'
        constraints = [
            models.UniqueConstraint(
                fields=['job_fair_id', 'recruiter_id', 'student_registration_number'], 
                name='unique_student_recruiter_attendance'
            )
        ]