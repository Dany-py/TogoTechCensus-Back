def save_user_profile(backend, user, response, *args, **kwargs):
    """
    Pipeline personnalisée pour sauvegarder les données spécifiques 
    depuis Google ou GitHub vers notre modèle Users.
    """
    if backend.name == 'google-oauth2':
        # Données Google
        user.avatar_url = response.get('picture', '')
        user.subId = response.get('sub', '')
        user.provider = 'google'
        # Google fournit souvent 'given_name' et 'family_name'
        if not user.name:
            user.name = f"{response.get('given_name', '')} {response.get('family_name', '')}".strip()

    elif backend.name == 'github':
        # Données GitHub
        user.avatar_url = response.get('avatar_url', '')
        user.subId = str(response.get('id', ''))
        user.provider = 'github'
        if not user.name:
            user.name = response.get('name') or response.get('login', '')

    user.save()
