from django.core.management.base import BaseCommand
from projects.models import Projects, Categories, Authors, Audiences
from django.utils.text import slugify
from utils import excel_extract_data

class Command(BaseCommand):
    help = 'Insère les données de la table project.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Début de l'importation..."))
        data = excel_extract_data()
        data_project = data.get('project', {})

        if not data_project:
            self.stdout.write(self.style.WARNING("Aucun projet trouvé dans le fichier."))
            return

        count = 0
        for key, value in data_project.items():
            if value[0] == 'Nom':
                continue

            if len(value) < 8:
                self.stdout.write(self.style.WARNING(f"Ligne '{key}' incomplète, ignorée."))
                self.stdout.write(self.style.WARNING(f"Ligne {key} : {value}"))
                continue

            # Sécurisation des valeurs
            name          = str(value[0]).strip()[:200]  if value[0] else None
            slug          = slugify(name)[:100]           if name else None
            short_desc    = str(value[1]).strip()[:300]  if value[1] else ''
            project_type  = str(value[3]).strip()[:100]  if value[3] else None
            stage         = str(value[5]).strip()[:100]  if value[5] else 'Unknown'
            needs         = str(value[6]).strip()[:100]  if value[6] else ''
            website       = str(value[7]).strip()         if value[7] else ''
            categorie_name = str(value[8]).strip()        if len(value) > 8 and value[8] else None
            author_name    = str(value[4]).strip()        if len(value) > 8 and str(value[4]).strip() != '-' else 'Owner'
            audience       = str(value[2]).strip()[:100]  if len(value) > 8 and value[2] else 'Everybody'

            if not name or not slug:
                self.stdout.write(self.style.WARNING(f"Ligne '{key}' sans nom valide, ignorée."))
                continue

            obj, created = Projects.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'short_description': short_desc,
                    'description': '',
                    'type': project_type,
                    'stage': stage,
                    'needs': needs,
                    'is_verified': True,
                    'website_url': website,
                }
            )

            if categorie_name:
                category, cat_created = Categories.objects.get_or_create(
                    name=categorie_name
                )
                if cat_created:
                    self.stdout.write(f"  ✔ Catégorie créée : {categorie_name}")
                obj.categories.add(category)

            if author_name:
                author, cat_author = Authors.objects.get_or_create(
                    name=author_name,
                    defaults={
                        'role': 'Developper',
                        'slug': slugify(author_name)
                    }
                )
                if cat_author:
                    self.stdout.write(f"  ✔ Autheur créée : {author_name}")
                obj.authors.add(author)

            if audience:
                audiances , aud = Audiences.objects.get_or_create(
                    name=audience,
                    defaults={
                        'project_id':obj.pk
                    }
                )
                if aud:
                    self.stdout.write(f"  ✔ Audience créée : {audience}")
                obj.audiences.add(audiances)

            if created:
                self.stdout.write(f"✔ Projet créé : {name}")
                count += 1
            else:
                self.stdout.write(self.style.NOTICE(f"— Projet existant : {name}"))

        self.stdout.write(self.style.SUCCESS(f"Terminé ! {count} nouveaux projets ajoutés."))