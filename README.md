# TogoTechCensus

API backend Django pour le recensement et le suivi des projets et acteurs technologiques au Togo.

---

## Stack technique

| Composant | Technologie |
|---|---|
| Framework | Django 6.0.2 |
| API REST | Django REST Framework 3.16.1 |
| WebSockets | Django Channels 4.3.2 + channels_redis |
| Base de données | PostgreSQL (via psycopg2) |
| Cache / Message broker | Redis 7 |
| Authentification OAuth2 | social-auth-app-django (Google & GitHub) |
| Serveur ASGI | Uvicorn |
| Variables d'environnement | python-dotenv |

---

## Architecture du projet

```
TogoTechCensus/
├── Census/                  # Racine Django
│   ├── manage.py
│   ├── .env                 # Variables d'environnement
│   ├── src/                 # Configuration du projet Django
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── asgi.py          # Point d'entrée ASGI (HTTP + WebSocket)
│   ├── users/               # Gestion des utilisateurs (modèle custom AbstractUser)
│   ├── projects/            # Gestion des projets tech (modèles, catégories, technologies, auteurs)
│   ├── notification/        # Système de notifications (in-app + WebSocket)
│   └── utils/               # Fonctions utilitaires partagées
├── requirements.txt
└── pyvenv.cfg
```

### Applications Django

#### `users`
- Modèle `Users` étendant `AbstractUser`
- Rôles : `USER` et `MODERATOR`
- Champs : `name`, `avatar_url`, `role`, `subId`, `provider`, `is_verified`
- Pipeline social auth personnalisée (`pipeline.py`)

#### `projects`
- Modèle principal `Projects` avec : description, classification (type, stage, needs, audiences), géolocalisation, métriques de vues, modération (`is_verified`, `is_archived`, `is_deleted`)
- Stades de projet : `Early`, `Growth`, `Maturity`, `Early/Growth`
- Relations many-to-many via tables intermédiaires :
  - `Categories` / `ProjectCategory`
  - `Technologies` / `ProjectTechnology`
  - `Authors` / `ProjectAuthor`
- Modèle `Updates` : journal des mises à jour de projet
- Modèle `Submissions` : workflow de soumission avec statuts `Pending`, `Approved`, `Rejected`
- Signals (`signals.py`) et permissions personnalisées (`permissions.py`)

#### `notification`
- Modèle `Notification` avec types : project_submitted/approved/rejected, comment, mention, system…
- Niveaux de priorité : low, medium, high, urgent
- `NotificationPreference` : préférences par utilisateur (email, in-app, heures silencieuses)
- `NotificationLog` : journal de livraison (email, in-app, push)
- Consumer WebSocket (`consumer.py`) avec routing dédié (`routing.py`)
- Middleware d'authentification par cookie (`middleware.py`)

---

## Routes API

| Préfixe | Application |
|---|---|
| `/admin/` | Interface d'administration Django |
| `/api/csrf/` | Récupération du token CSRF |
| `/api/auth/` | OAuth2 social auth (Google, GitHub) |
| `/api/users/` | Gestion des utilisateurs |
| `/api/projects/` | Gestion des projets |
| `/api/notification/` | Notifications + WebSocket |

---

## Variables d'environnement

Créer un fichier `.env` dans le dossier `Census/` :

```env
SECRET_KEY=your-secret-key

# Base de données PostgreSQL
ENGINE=django.db.backends.postgresql
NAME=census
USER=postgres
PASSWORD=your-password
HOST=localhost
DB_PORT=5432

# Environnement (development | production)
PYTHON_ENV=development

# Frontend (CORS & CSRF)
FRONTEND_URL=http://localhost:5173

# OAuth2 Google
GOOGLE_OAUTH2_KEY=your-google-client-id
GOOGLE_OAUTH2_SECRET=your-google-client-secret

# OAuth2 GitHub
GITHUB_OAUTH2_ID=your-github-client-id
GITHUB_OAUTH2_SECRET=your-github-client-secret

# Redirections OAuth2
SOCIAL_AUTH_LOGIN_REDIRECT_URL=http://localhost:5173/dashboard
SOCIAL_AUTH_LOGIN_ERROR_URL=http://localhost:5173/login?error=true
LOGOUT_REDIRECT_URL=http://localhost:5173/

# Email (SMTP)
EMAIL_HOST=smtp.mailtrap.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_SENDER=support@yourdomain.com
```

> **Important** : Ne jamais committer le fichier `.env` en production. Le `.gitignore` doit l'exclure.

---

## Installation

### Prérequis

- Python 3.11+
- PostgreSQL
- Redis (pour Channels)

### Étapes

1. **Cloner le dépôt**
   ```bash
   git clone <url-du-repo>
   cd TogoTechCensus
   ```

2. **Créer et activer l'environnement virtuel**
   ```bash
   python -m venv venv

   # Windows
   .\venv\Scripts\activate

   # Linux / macOS
   source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement**
   ```bash
   # Copier et compléter le fichier .env dans Census/
   cp Census/.env.example Census/.env
   ```

5. **Appliquer les migrations**
   ```bash
   cd Census
   python manage.py migrate
   ```

6. **Créer un super-utilisateur (optionnel)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Lancer le serveur de développement**

   Le projet utilise **ASGI** (Uvicorn) pour supporter les WebSockets :
   ```bash
   cd Census
   uvicorn src.asgi:application --host 127.0.0.1 --port 8000 --reload
   ```

   > Le serveur `manage.py runserver` peut être utilisé mais **ne supporte pas les WebSockets**.

---

## Redis (requis pour les WebSockets)

Assurez-vous que Redis tourne localement sur le port par défaut `6379` :

```bash
# Linux
redis-server

# Windows (via WSL ou Redis for Windows)
redis-server
```

---

## Tests

```bash
cd Census
python manage.py test users
python manage.py test projects
python manage.py test notification
```

---

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.
