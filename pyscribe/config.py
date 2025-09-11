import yaml
from typing import NamedTuple


class Config(NamedTuple):
    save_path: str
    default_device: str

    model: str
    prompt: str
    language: str
    remove_silence: bool


def load_config() -> Config:
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    return Config(**config)


config: Config = load_config()
