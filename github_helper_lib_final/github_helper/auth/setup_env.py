import os
import tempfile

def setup_env(
    app_id: str = None,
    installation_id: str = None,
    pem_path: str = None,
    pem_str: str = None,
    personal_token: str = None
) -> None:
    """
    Configura as credenciais do GitHub para uso interno via variáveis de ambiente.
    """
    if personal_token:
        os.environ["GITHUB_PERSONAL_TOKEN"] = personal_token

    if app_id and installation_id:
        os.environ["GITHUB_APP_ID"] = app_id
        os.environ["GITHUB_INSTALLATION_ID"] = installation_id

        if pem_path:
            os.environ["GITHUB_PEM_FILE"] = pem_path
        elif pem_str:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pem", mode="w")
            temp_file.write(pem_str)
            temp_file.close()
            os.environ["GITHUB_PEM_FILE"] = temp_file.name
