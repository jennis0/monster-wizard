import configparser
import os

from typing import Dict

from boto3 import setup_default_session

from utils.aws import setup_aws_config

def setup_default_config() -> Dict[str, str]:
    '''Generate default config section'''
    return {
        "cache":".cache"
    }

def create_new_config() -> configparser.ConfigParser:
    '''Interact with user to create a new config file'''
    config = configparser.ConfigParser()

    result = input("No config file found. Do you want to setup AWS credentials? [y|n]")
    if result.strip().lower() == 'y':
        config["aws"] = setup_aws_config()

    config["default"] = setup_default_config()

    return config

def get_config(config_path: str) -> configparser.ConfigParser:
    '''Load a config file from the given path or generate a new one if it does not exists'''
    #If config doesn't exist, make one!
    if not os.path.exists(config_path):
        config = create_new_config()
        with open(config_path, 'w') as f:
            config.write(f)
    else:
        #Otherwise just read it in
        config = configparser.ConfigParser()
        config.read(config_path)
    
    return config


