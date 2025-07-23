from .content import GitContent
from github.Issue import Issue

def create_issue_if_not_exists(
    content: GitContent,
    title: str,
    body: str,
    labels: list[str]
) -> str | None:
    """
    Cria uma issue no repositório caso ainda não exista uma com as mesmas labels.

    :param content: GitContent com o repositório.
    :param title: Título da issue.
    :param body: Corpo da issue.
    :param labels: Lista de labels (ex: ["bug", "urgent", "id:123"]).
    :return: URL da issue criada ou existente.
    """
    try:
        label_query = ",".join(labels)
        issues = content.repository.get_issues(state="open", labels=label_query)

        if issues.totalCount > 0:
            return issues[0].html_url

        issue: Issue = content.repository.create_issue(
            title=title,
            body=body,
            labels=labels
        )
        return getattr(issue, "html_url", None)

    except Exception as e:
        print(f"[create_issue_if_not_exists] Erro ao criar/verificar issue: {e}")
        return None