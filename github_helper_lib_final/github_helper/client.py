from .auth.chain import resolve_token
from .base import Git

class GitHubClient(Git):
    def __init__(self, personal_token: str | None = None):
        token = resolve_token(personal_token)
        super().__init__(token)
