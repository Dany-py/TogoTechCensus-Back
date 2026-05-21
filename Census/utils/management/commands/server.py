import os
import uvicorn
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db.models import Count
from projects.models import Projects

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

    def handle(self, *args, **options):
        self.db_init()
        call_command('create_admin')
        self.collect_staticfiles()   # ← parenthèses !
        uvicorn.run(
            'src.asgi:application',
            lifespan='off',
            host=options['host'],
            port=options['port'],
            reload=options['reload'],
        )