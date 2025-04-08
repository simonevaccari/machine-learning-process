from pathlib import Path
from loguru import logger
import yaml
from .config import config_dict
from tile_based_training.utils.common import create_directories


def write_yaml(path_to_yaml: Path, data):
    try:
        with path_to_yaml.open("w") as yaml_file:
            yaml.dump(data, yaml_file)

        logger.info(f"YAML file: {path_to_yaml} written successfully")

    except Exception as e:
        logger.error(f"Error writing to YAML file {path_to_yaml}: {e}")
        raise e


create_directories(["config"])
write_yaml(Path("config/config.yaml"), data=config_dict)

CONFIG_FILE_PATH = Path("config/config.yaml")
PARAMS_FILE_PATH = Path("params.yaml")
