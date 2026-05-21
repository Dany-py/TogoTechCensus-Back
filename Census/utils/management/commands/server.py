import uvicorn
import os
from django.core.management.base import BaseCommand
from django.db.models import Count
from projects.models import Projects
from django.core.management import call_command

REQUIRED_PROJECT_COUNT = 92 | 93

class Command(BaseCommand):
    help = 'Run server using uvicorn + ASGI app'

    def add_arguments(self, parser):
        parser.add_argument('--host', default=os.getenv('SERVER_HOST', '127.0.0.1'))
        parser.add_argument('--port', type=int, default=int(os.getenv('SERVER_PORT', 8000)))
        parser.add_argument('--reload', action='store_true', default= os.getenv('PYTHON_ENV') == 'development')

    def db_init(self):
        count = Projects.objects.filter(is_verified=True).aggregate(
            total_active=Count('id')
        ).get('total_active', 0)

        if count < REQUIRED_PROJECT_COUNT:
            try:
                call_command('project')
                self.stdout.write("DB initialization successful.")
            except Exception as e:
                self.stderr.write(f"Initialization failed : {e}")

    def handle(self, *args, **options):
        self.db_init()
        call_command('create_admin')
        uvicorn.run(
            'src.asgi:application',
            lifespan='off',
            host=options['host'],
            port=options['port'],
            reload=options['reload'],
        )