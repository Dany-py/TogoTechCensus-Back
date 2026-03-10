# TogoTechCensus

TogoTechCensus est un projet Django conçu pour le recensement et le suivi des technologies et des projets tech au Togo.

## Fonctionnalités

- Gestion des projets tech
- Annuaire des utilisateurs et des experts
- Suivi des statistiques du secteur technologique

## Architecture du Projet

Le projet est structuré comme suit :
- `Census/`: Dossier principal regroupant les applications Django.
    - `projects/`: Gestion des projets technologiques.
    - `users/`: Gestion des utilisateurs.
    - `utils/`: Fonctions utilitaires partagées.
- `requirements.txt`: Liste des dépendances Python.

## Installation

1. **Cloner le projet**
   ```bash
   git clone <url-du-repo>
   cd TogoTechCensus
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   ```

3. **Activer l'environnement virtuel**
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - Linux/macOS:
     ```bash
     source venv/bin/activate
     ```

4. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

5. **Appliquer les migrations**
   ```bash
   cd Census
   python manage.py migrate
   ```

6. **Lancer le serveur de développement**
   ```bash
   python manage.py runserver
   ```

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.
