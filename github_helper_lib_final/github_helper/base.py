from github import Github
from github.PaginatedList import PaginatedList
from .content import GitContent

class Git:
    URL = "https://api.github.com/"

    def __init__(self, token: str):
        self.git = Github(login_or_token=token, base_url=self.URL, verify=False)

    def search(self, query: str) -> PaginatedList:
        return self.git.search_code(query)

    def get_content_by_url(self, url: str) -> GitContent | None:
        if not isinstance(url, str) or len(url) == 0:
            return None

        parts = url.split('/')
        usuario = parts[3]
        repositorio = parts[4]
        branch = parts[6]
        caminho_arquivo = '/'.join(parts[7:]).split('#')[0]

        repo = self.git.get_repo(f"{usuario}/{repositorio}")
        file_content = repo.get_contents(caminho_arquivo, ref=branch)
        return GitContent(file_content)
