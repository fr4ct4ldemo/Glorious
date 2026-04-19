async def does_user_meet_requirements(user_roles, guild_roles, service_input):
    try:
        user_ids = [role.id for role in user_roles]
        for role in guild_roles:
            if role['id'] in user_ids:
                if service_input in role.get('gen-access', []) or "all" in role.get('gen-access', []):
                    return True
        return False
    except Exception:
        return False