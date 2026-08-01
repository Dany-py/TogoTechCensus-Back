import os
import uvicorn
import time
import threading
import httpx
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db.models import Count
from projects.models import Projects
from sched import scheduler

MIN_PROJECT_COUNT = 92

class Command(BaseCommand):
    help = 'Run server using uvicorn + ASGI app'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize the scheduler once in the instance
        self.sched = scheduler(time.time, time.sleep)

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
        """ 
        Attempts to ping the frontend. On success (200), schedules the next check in 10 min.
        On failure, retries every 30 seconds until it works.
        """
        url_target = 'https://togotechcensus-dev.up.railway.app/'
        try:
            self.stdout.write(f"Pinging frontend: {url_target}")
            response = httpx.get(url_target, timeout=15.0) # Slightly longer timeout for wake-up
            
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS("Frontend is awake!"))
                # Success! Schedule the next routine check in 10 minutes
                self.plan_next_frontend_job()
            else:
                self.stdout.write(self.style.WARNING(f"Frontend responded with status: {response.status_code}"))
                # Failure (e.g., 502, 503 during wake-up): Retry in 30 seconds
                self.stdout.write("Retrying wake-up in 30 seconds...")
                self.sched.enter(delay=30, priority=1, action=self.revival_front)

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error occurred during frontend ping: {e}"))
            # Network error (e.g., server not responding at all): Retry in 30 seconds
            self.stdout.write("Network error. Retrying wake-up in 30 seconds...")
            self.sched.enter(delay=30, priority=1, action=self.revival_front)
    
    def plan_next_frontend_job(self):
        """ Decision logic: should we schedule another ping? """
        frontend_url = os.getenv('FRONTEND_URL', '')
        
        if not frontend_url:
            self.stdout.write("FRONTEND_URL not defined. No wake-up.")
            return

        # Security to prevent crash if URL is unusual
        if 'railway' in frontend_url or 'app' in frontend_url:
            current_time = time.localtime()
            day_of_week = current_time.tm_wday
            current_hour = current_time.tm_hour

            # Monday (0) to Friday (4) and between 7am and 6:59pm
            if day_of_week < 5 and 7 <= current_hour < 19:
                interval = 10 * 60  # 10 minutes
                self.sched.enter(delay=interval, priority=1, action=self.revival_front)
                self.stdout.write(f"Next ping scheduled in 10 minutes.")
            else:
                # If outside working hours, check again later (e.g., in 30 mins) without pinging
                self.sched.enter(delay=30 * 60, priority=1, action=self.plan_next_frontend_job)
                self.stdout.write(f"Outside working hours (day={day_of_week}, hour={current_hour}h). Pausing for 30min.")
        else:
            self.stdout.write("Frontend URL is not on Railway, no wake-up necessary.")

    def start_scheduler(self):
        """ Launch the scheduler in a SINGLE dedicated thread that will run in the background. """
        self.plan_next_frontend_job()
        # Only launch the scheduler loop in a thread once
        if not self.sched.empty():
            thread = threading.Thread(target=self.sched.run, daemon=True)
            thread.start()
            self.stdout.write(self.style.SUCCESS("Background scheduler started successfully."))
            
    def handle(self, *args, **options):
        self.db_init()
        call_command('create_admin')
        self.collect_staticfiles()
        
        # Launch the ping system in the background
        self.start_scheduler()
        
        # Launch Uvicorn (blocking, keeps the process alive)
        uvicorn.run(
            'src.asgi:application',
            lifespan='off',
            host=options['host'],
            port=options['port'],
            reload=options['reload'],
        )