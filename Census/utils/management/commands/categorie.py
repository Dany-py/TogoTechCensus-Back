
from django.core.management.base import BaseCommand
from Census.utils import excel_extract_data
from projects.models import Categories

class Command(BaseCommand):
    help = 'Insère les données de la table catégories'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Début de l'importation..."))
        
        data = excel_extract_data()
        data_categories = data.get('categories', [])

        if not data_categories:
            self.stdout.write(self.style.WARNING("Aucune catégorie trouvée dans le fichier."))
            return

        count = 0
        for category_name in data_categories:
                obj, created = Categories.objects.get_or_create(name=category_name)
                
                if created:
                    self.stdout.write(f"Enregistrement de la catégorie : {category_name}")
                    count += 1
                else:
                    self.stdout.write(self.style.NOTICE(f"La catégorie '{category_name}' existe déjà."))

        self.stdout.write(self.style.SUCCESS(f"Terminé ! {count} nouvelles catégories ajoutées."))