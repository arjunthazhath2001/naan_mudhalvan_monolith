from django.core.management.base import BaseCommand
from program_managers.models import ProgramManager

class Command(BaseCommand):
    help = 'Creates program managers for all districts'

    def handle(self, *args, **options):
        districts = [
            "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore", 
            "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kancheepuram", 
            "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai", 
            "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai", 
            "Ramanathapuram", "Ranipet", "Salem", "Sivaganga", "Tenkasi", "Thanjavur", 
            "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli", "Tirupattur", 
            "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Tiruvarur", "Vellore", 
            "Viluppuram", "Virudhunagar"
        ]        
        for district in districts:
            username = f"manager_{district.lower().replace(' ', '_')}"
            password = f"pass_{district.lower().replace(' ', '_')}"
            
            manager, created = ProgramManager.objects.get_or_create(
                username=username,
                defaults={
                    'password': password,
                    'district': district,
                    'email': f"{username}@example.com"
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created program manager for {district}: {username} / {password}'))
            else:
                self.stdout.write(self.style.WARNING(f'Program manager for {district} already exists'))