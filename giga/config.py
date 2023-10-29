import os
from getpass import getpass
from pathlib import Path
from tempfile import gettempdir
from typing import Any

from click import UsageError

CONFIG_FOLDER = os.path.expanduser("~/.config")
GIGA_SHELL_CONFIG_FOLDER = Path(CONFIG_FOLDER) / "gigashell"
GIGA_SHELL_CONFIG_PATH = GIGA_SHELL_CONFIG_FOLDER / ".gigatrc"
ROLE_STORAGE_PATH = GIGA_SHELL_CONFIG_FOLDER / "roles"
CHAT_CACHE_PATH = Path(gettempdir()) / "chat_cache"
CACHE_PATH = Path(gettempdir()) / "cache"

# TODO: Refactor ENV variables with GIGA_ prefix.
DEFAULT_CONFIG = {
    # TODO: Refactor it to CHAT_STORAGE_PATH.
    "CHAT_CACHE_PATH": os.getenv("CHAT_CACHE_PATH", str(CHAT_CACHE_PATH)),
    "CACHE_PATH": os.getenv("CACHE_PATH", str(CACHE_PATH)),
    "CHAT_CACHE_LENGTH": int(os.getenv("CHAT_CACHE_LENGTH", "100")),
    "CACHE_LENGTH": int(os.getenv("CHAT_CACHE_LENGTH", "100")),
    "REQUEST_TIMEOUT": int(os.getenv("REQUEST_TIMEOUT", "60")),
    "DEFAULT_MODEL": os.getenv("DEFAULT_MODEL", "GigaChat70:latest"),
    "DEFAULT_COLOR": os.getenv("DEFAULT_COLOR", "magenta"),
    "ROLE_STORAGE_PATH": os.getenv("ROLE_STORAGE_PATH", str(ROLE_STORAGE_PATH)),
    "SYSTEM_ROLES": os.getenv("SYSTEM_ROLES", "false"),
    "DEFAULT_EXECUTE_SHELL_CMD": os.getenv("DEFAULT_EXECUTE_SHELL_CMD", "false"),
    "DISABLE_STREAMING": os.getenv("DISABLE_STREAMING", "false")
    # New features might add their own config variables here.
}


class Config(dict):  # type: ignore
    def __init__(self, config_path: Path, **defaults: Any):
        self.config_path = config_path

        if self._exists:
            self._read()
            has_new_config = False
            for key, value in defaults.items():
                if key not in self:
                    has_new_config = True
                    self[key] = value
            if has_new_config:
                self._write()
        else:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            # Don't write API key to config file if it is in the environment.
            if not defaults.get("GIGA_CREDENTIALS") and not os.getenv("GIGA_CREDENTIALS"):
                __username = input("Please enter GigaChat credentials: ")
                defaults["GIGA_CREDENTIALS"] = __credentials
            '''
            if not defaults.get("GIGA_USERNAME") and not os.getenv("GIGA_USERNAME"):
                __username = input("Please enter GigaChat username: ")
                defaults["GIGA_USERNAME"] = __username

            if not defaults.get("GIGA_PASSWORD") and not os.getenv("GIGA_PASSWORD"):
                __password = getpass(prompt="Please enter GigaChat password: ")
                defaults["GIGA_PASSWORD"] = __password

            if not defaults.get("GIGACHAT_API_HOST") and not os.getenv(
                "GIGACHAT_API_HOST"
            ):
                __default_host = "https://wmapi-dev.saluteai-pd.sberdevices.ru/v1/"
                __host = input(
                    f"Please enter GigaChat host with 70b model [{__default_host}]: "
                )
                if __host == "":
                    __host = __default_host
                defaults["GIGACHAT_API_HOST"] = __host
                '''
            super().__init__(**defaults)
            self._write()

    @property
    def _exists(self) -> bool:
        return self.config_path.exists()

    def _write(self) -> None:
        with open(self.config_path, "w", encoding="utf-8") as file:
            string_config = ""
            for key, value in self.items():
                string_config += f"{key}={value}\n"
            file.write(string_config)

    def _read(self) -> None:
        with open(self.config_path, "r", encoding="utf-8") as file:
            for line in file:
                if not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    self[key] = value

    def get(self, key: str) -> str:  # type: ignore
        # Prioritize environment variables over config file.
        value = os.getenv(key) or super().get(key)
        if not value:
            raise UsageError(f"Missing config key: {key}")
        return value


cfg = Config(GIGA_SHELL_CONFIG_PATH, **DEFAULT_CONFIG)
