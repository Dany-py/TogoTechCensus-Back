import os
import uvicorn
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db.models import Count
from projects.models import Projects
from sched import scheduler
import httpx
import time

MIN_PROJECT_COUNT = 92

class Command(BaseCommand):
    help = 'Run server using uvicorn + ASGI app'

    def add_arguments(self, parser):
        parser.add_argument('--host', default=os.getenv('SERVER_HOST', '127.0.0.1'))
        parser.add_argument('--port', type=int, default=int(os.getenv('SERVER_PORT', 8000)))
        parser.add_argument('--reload', action='store_true', default=os.getenv('PYTHON_ENV') == 'development')

    def db_init(self):
        count = Projects.objects.filter(is_verified=True).aggregate(
            total_active=Count('id')
        ).get('total_active', 0)

        if count < MIN_PROJECT_COUNT:
            try:
                call_command('project')
                self.stdout.write(self.style.SUCCESS("DB initialization successful."))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Initialization failed: {e}"))

    def collect_staticfiles(self):
        static_root = settings.STATIC_ROOT
        if static_root and (not os.path.exists(static_root) or not os.listdir(static_root)):
            self.stdout.write("Collecting static files...")
            call_command('collectstatic', interactive=False)
            self.stdout.write(self.style.SUCCESS("Static files collected."))
            
    def revival_front(self):
        try:
            response = httpx.get('https://togotechcensus-dev.up.railway.app/')
            if response.status_code != 200:
                self.revival_front()
        except Exception as e:
            print(f'Error occured : {e}')
        finally:
            self.frontend_job_schedule()

    def frontend_job_schedule(self):
        temps_actuel = time.localtime()
        jour_semaine = temps_actuel.tm_wday
        heure_actuelle = temps_actuel.tm_hour

        frontSched = scheduler(time.time, time.sleep)
        url = os.getenv('FRONTEND').split('.')

        if 'railway' | 'app' in url:
            if jour_semaine < 5 and 7 <= heure_actuelle < 19:
                interval = 10 * 60
                frontSched.enter(
                    delay=interval,
                    priority=1,
                    action=self.revival_front
                )
                frontSched.run()
            else:
                print(f"Hors plage horaire — pas de ping (jour={jour_semaine}, heure={heure_actuelle}h)")
        else:
            print(f"L'URL frontend n'est pas hébergée sur Railway, pas de revival nécessaire.")
            
    def handle(self, *args, **options):
        self.db_init()
        call_command('create_admin')
        self.collect_staticfiles()
        self.frontend_job_schedule()
        uvicorn.run(
            'src.asgi:application',
            lifespan='off',
            host=options['host'],
            port=options['port'],
            reload=options['reload'],
        )