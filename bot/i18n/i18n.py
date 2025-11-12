import os
from pathlib import Path
from typing import Any
import ruamel.yaml


class I18n:
    def __init__(self, yaml_file_path: Path | os.PathLike | str):  # , format_values: dict[str, Any]
        self.path = Path(yaml_file_path)
        self.data = self._load_language_file()
        # self.format_values = {}

    def _load_language_file(self) -> dict:
        yaml = ruamel.yaml.YAML()

        if not self.path.exists():
            return {}

        with self.path.open("r", encoding="utf-8") as file:
            return yaml.load(file) or {}

    def __call__(self, path: str) -> Any:
        keys = path.split(".")
        data = self.data
        for current_key in keys:
            try:
                if isinstance(data, dict):
                    data = data[current_key]
                elif isinstance(data, list):
                    data = data[int(current_key)]
                else:
                    return path
            except (ValueError, IndexError, KeyError):
                return path
        return data  # .format(**self.format_values)

    def __getitem__(self, path: str):
        return self.__call__(path)

