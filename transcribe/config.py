import yaml
from typing import NamedTuple


class Config(NamedTuple):
    model: str
    initial_prompt: str
    language: str


def load_config() -> Config:
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    return Config(**config)


config: Config = load_config()
