import os, pathlib, configparser, time, jwt, requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

class CredentialsNotFound(Exception): ...

class EnvProvider:
    def resolve(self) -> str | None:
        if token := os.getenv("GITHUB_PERSONAL_TOKEN"):
            return token
        app_id = os.getenv("GITHUB_APP_ID")
        inst_id = os.getenv("GITHUB_INSTALLATION_ID")
        pem_path = os.getenv("GITHUB_PEM_FILE")
        if all([app_id, inst_id, pem_path]):
            return self._get_installation_token(app_id, inst_id, pem_path)
        return None

    def _get_installation_token(self, app_id, inst_id, pem_path):
        with open(pem_path, "r") as f:
            private_key = serialization.load_pem_private_key(
                f.read().encode(), password=None, backend=default_backend()
            )
        now = int(time.time())
        payload = {"iat": now, "exp": now + 600, "iss": app_id}
        jwt_token = jwt.encode(payload, private_key, algorithm="RS256")
        headers = {"Authorization": f"Bearer {jwt_token}",
                   "Accept": "application/vnd.github+json"}
        r = requests.post(
            f"https://api.github.com/app/installations/{inst_id}/access_tokens",
            headers=headers
        )
        r.raise_for_status()
        return r.json()["token"]

class FileProvider:
    def resolve(self) -> str | None:
        path = pathlib.Path("~/.github-helper/credentials").expanduser()
        if not path.exists():
            return None
        config = configparser.ConfigParser()
        config.read(path)
        if "default" not in config:
            return None
        profile = config["default"]
        if "personal_token" in profile:
            return profile["personal_token"]
        if {"app_id", "installation_id", "pem_file"} <= profile.keys():
            with open(profile["pem_file"], "r") as f:
                return EnvProvider()._get_installation_token(
                    profile["app_id"], profile["installation_id"], f.name)
        return None
