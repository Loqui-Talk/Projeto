from .providers import EnvProvider, FileProvider, CredentialsNotFound

def resolve_token(explicit_token: str | None = None) -> str:
    if explicit_token:
        return explicit_token
    for provider in (EnvProvider(), FileProvider()):
        token = provider.resolve()
        if token:
            return token
    raise CredentialsNotFound("Token não encontrado. Configure via argumento, env ou arquivo.")
