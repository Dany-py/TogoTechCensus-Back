
"""Keep the Render projects awake while this management command is running."""

import requests
import sched
import time
from django.core.management.base import BaseCommand

render_links = [
    "https://togotechcensus-back.onrender.com",
]

def revival(urls, output):
    results = {}
    for url in urls:
        try:
            res = requests.get(url, timeout=10) 
            results[url] = res.status_code == 200
            output(f"Ping réussi pour {url}. Statut: {res.status_code}")
        except requests.RequestException as e:
            results[url] = False
            output(f"Échec du ping pour {url}. Erreur: {e}")
    return results


class Command(BaseCommand):
    help = "Keep the configured Render projects awake."

    def handle(self, *args, **options):
        scheduler = sched.scheduler(time.time, time.sleep)

        def ping_and_schedule():
            revival(render_links, self.stdout.write)
            scheduler.enter(10 * 60, 1, ping_and_schedule)

        scheduler.enter(0, 1, ping_and_schedule)
        self.stdout.write("Revival service started. Press Ctrl+C to stop.")

        try:
            scheduler.run()
        except KeyboardInterrupt:
            self.stdout.write("\nRevival service stopped.")