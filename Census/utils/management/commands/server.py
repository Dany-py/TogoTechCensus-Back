import uvicorn
import os
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Run server using uvicorn + ASGI app'

    def add_arguments(self, parser):
        parser.add_argument('--host', default=os.getenv('SERVER_HOST'))
        parser.add_argument('--port', type=int, default=os.getenv('SERVER_PORT'))
        parser.add_argument('--reload', action='store_true', default=True)

    def handle(self, *args, **options):
        uvicorn.run(
            'src.asgi:application',
            host=options['host'],
            port=options['port'],
            reload=options['reload'],
        )