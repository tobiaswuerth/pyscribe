import yaml
from typing import NamedTuple


class Config(NamedTuple):
    save_path: str
    default_device: str
    segment_duration: int
    model: str
    prompt: str
    language: str
    finish_processing_on_exit: bool
    combine_on_exit: bool
    remove_after_combine: bool
    split_on_silence: bool
    min_silence_duration: float
    silence_calibration_window: int
    hardcut_threshold: int
    consider_noise_silent_percentile: int


def load_config() -> Config:
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    return Config(**config)


config: Config = load_config()
