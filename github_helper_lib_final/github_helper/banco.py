from .base import Git
from .content import GitContent
from github.ContentFile import ContentFile

class bancoGithub(Git):
    ORG = "banco"

    def __init__(self, token: str):
        super().__init__(token)

    def search(self, query: str):
        return super().search(f"{query} org:{self.ORG}")

    def search_repository_content(self, repo_name: str, file_path: str = "README.md") -> GitContent | None:
        repo = self.git.get_repo(f"{self.ORG}/{repo_name}")
        file_content: ContentFile = repo.get_contents(file_path)
        if isinstance(file_content, list):
            file_content = file_content[0]
        return GitContent(file_content)
