from django.db import models

class ProgramManager(models.Model):
    manager_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    
    class Meta:
        db_table = 'program_managers'
        
    def __str__(self):
        return f"{self.username} - {self.district}"
