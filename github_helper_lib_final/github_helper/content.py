from github.ContentFile import ContentFile
from github.Commit import Commit
from github.Repository import Repository

class GitContent:
    def __init__(self, content: ContentFile):
        self.content = content

    @property
    def text(self) -> str:
        return self.content.decoded_content.decode()

    @property
    def readme(self) -> str:
        return self.content.repository.get_readme().decoded_content.decode()

    @property
    def last_commit(self) -> Commit | None:
        commits = self.content.repository.get_commits(path=self.content.path)
        return commits[0] if commits.totalCount > 0 else None

    @property
    def url_code(self) -> str:
        return self.content.html_url

    @property
    def path(self) -> str:
        return self.content.path

    @property
    def repository(self) -> Repository:
        return self.content.repository
