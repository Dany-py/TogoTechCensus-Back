from django.core.management.base import BaseCommand
from projects.models import Projects, Categories, Authors, Technologies
from django.utils.text import slugify
from utils import excel_extract_data, get_sync_favicon
from datetime import datetime
import random
import asyncio

import subprocess

try:
    # Exécute la commande et lève une exception si elle échoue (code de retour différent de 0)
    result = subprocess.run(
        ["echo", "Bonjour depuis le CLI"], 
        check=True, 
        capture_output=True, 
        text=True
    )
    
    # On récupère ce que la commande a écrit dans le terminal
    print("Sortie du CLI :", result.stdout)

except subprocess.CalledProcessError as e:
    print(f"La commande a échoué avec le code {e.returncode}")
    print("Erreur :", e.stderr)

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

            type = slugify(str(value[4]).strip())[:100]
            
            # Sécurisation des valeurs
            name          = str(value[0]).strip()[:200]         if value[0] else None
            slug          = slugify(name)[:100]                 if name else None
            description   = str(value[1])[:2000]                 if value[1] else ''
            short_desc    = str(value[2]).strip()[:300]         if value[2] else ''
            audience      = str(value[3]).strip()[:100]         if len(value) > 10 and value[3] else 'Everybody'
            project_type  = slugify(str(value[4]).strip())[:100]         if value[4] else None
            author_name   = str(value[5]).split(', ')           if len(value) > 10 and str(value[4]).strip() != '-' else 'Owner'
            stage         = str(value[6]).strip()[:100]         if value[6] else 'Unknown'
            technologies  = str(value[7]).split(', ')
            needs         = str(value[8]).strip()[:100]         if value[7] else ''
            website       = str(value[9]).strip()               if value[8] and project_type != 'open-source' else ''
            github        = str(value[9]).strip()               if value[8] and project_type == 'open-source' else ''
            categorie_name = slugify(str(value[10]).strip())     if len(value) > 10 and value[10] else None
            
            
            if project_type == 'open-source':
                logo_url      = asyncio.run(get_sync_favicon('github.com'))
            else:
                logo_url      = asyncio.run(get_sync_favicon(website))   if website else ''

            if not name or not slug:
                self.stdout.write(self.style.WARNING(f"Ligne '{key}' sans nom valide, ignorée."))
                continue

            obj, created = Projects.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'description': description,
                    'short_description': short_desc,
                    'type': project_type,
                    'stage': stage,
                    'audiences': audience,
                    'logo_url': logo_url,
                    'needs': needs,
                    'is_verified': True,
                    'verified_at': datetime.now(),
                    'artificial_view': random.randint(50, 100),
                    'website_url': website,
                    'github_url': github      
                }
            )

            if categorie_name:
                category, cat_created = Categories.objects.get_or_create(
                    name=categorie_name
                )
                if cat_created:
                    self.stdout.write(f"  ✔ Catégorie créée : {categorie_name}")
                obj.categories.add(category)

            if technologies:
                for techno in technologies:
                    tech_slug = Technologies.objects.filter(slug=slugify(techno))
                    tech_id = Technologies.objects.filter(slug=slugify(techno)).values_list('id', flat=True).first()                    
                    if tech_slug:
                        obj.technologies.add(tech_id)
                        pass
                    else:
                        tech, tech_created = Technologies.objects.get_or_create(
                            name=techno,
                            slug= slugify(techno)
                        )
                        if tech_created:
                            self.stdout.write(f"  ✔ Techno créée : {techno}")
                        obj.technologies.add(tech)
                    
            if author_name:
                for auth in author_name:
                
                    if auth == '-':
                        auth = 'owner'
                        author, cat_author = Authors.objects.get_or_create(
                            name=auth,
                            defaults={
                                'role': 'developper',
                                'slug': slugify(auth)
                            }
                        )
                        if cat_author:
                            self.stdout.write(f"  ✔ Autheur créée : {auth}")
                        obj.authors.add(author)
                        
                    author, cat_author = Authors.objects.get_or_create(
                        name=auth,
                        defaults={
                            'role': 'developper',
                            'slug': slugify(auth)
                        }
                    )
                    if cat_author:
                        self.stdout.write(f"  ✔ Autheur créée : {auth}")
                    obj.authors.add(author)

            if created:
                self.stdout.write(f"✔ Projet créé : {name}")
                count += 1
            else:
                self.stdout.write(self.style.NOTICE(f"— Projet existant : {name}"))

        self.stdout.write(self.style.SUCCESS(f"Terminé ! {count} nouveaux projets ajoutés."))