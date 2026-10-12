from social_core.exceptions import AuthForbidden

from .models import Users


def prevent_duplicate_email(backend, details, user=None, *args, **kwargs):
    # L'utilisateur est déjà connecté : il peut associer un nouveau provider.
    if user is not None:
        return None

    email = (details.get("email") or "").strip()
    if email and Users.objects.filter(email__iexact=email).exists():
        raise AuthForbidden(
            backend,
            "Un compte existe déjà avec cette adresse. "
            "Connectez-vous à ce compte pour associer ce provider.",
        )

    return None


def save_user_profile(backend, user, response, *args, **kwargs):
    """
    Pipeline personnalisée pour sauvegarder les données spécifiques 
    depuis Google ou GitHub vers notre modèle Users.
    """
    users = Users.objects.all()
    user_exist = users.filter(email=user.email)

    if not user_exist and backend.name == 'google-oauth2':
        # Données Google
        user.avatar_url = response.get('picture', '')
        user.subId = response.get('sub', '')
        user.provider = 'google'
        # Google fournit souvent 'given_name' et 'family_name'
        if not user.name:
            user.name = f"{response.get('given_name', '')} {response.get('family_name', '')}".strip()

    elif not user_exist and backend.name == 'github':
        # Données GitHub
        user.avatar_url = response.get('avatar_url', '')
        user.subId = str(response.get('id', ''))
        user.provider = 'github'
        if not user.name:
            user.name = response.get('name') or response.get('login', '')

    user.save()
