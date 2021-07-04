import configparser
import argparse
import os

from typing import Dict

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

def get_config(args : Dict[str, str]) -> configparser.ConfigParser:
    '''Load a config file from the given path or generate a new one if it does not exists'''
    #If config doesn't exist, make one!
    if not os.path.exists(args.config):
        config = create_new_config()
        with open(args.config, 'w') as f:
            config.write(f)
    else:
        #Otherwise just read it in
        config = configparser.ConfigParser()
        config.read(args.config)

    if not config.has_section("default"):
        config.add_section("default")

    if args.cache:
        config.set("default", "cache", args.cache)
    
    if args.logs:
        config.set("default", "logdir", args.logs)
    
    return config

def get_argparser() -> argparse.ArgumentParser:
    '''Creates command line argument parser to control the app'''

    parser = argparse.ArgumentParser(
        description="Extract 5e statblocks from images and PDFs"
    )
    parser.add_argument("target", type=str, help="Image or PDF to search for monster statblocks")
    parser.add_argument("--source", "-s", type=str, help="Override source label for the statblocks processed")
    parser.add_argument("--authors", "-a", nargs='*', help="Override author label for the processed data")
    parser.add_argument("--url", "-u", type=str, help="Override URL label for processed data")
    parser.add_argument("--output", "-o", type=str, help="Output JSON file containing statblocks", default=None)
    parser.add_argument("--output-format", '-f', type=str, help="Output format. Options are 'default'", default='default')
    parser.add_argument("--cache", "-C", type=str, default=".cache", help="Local cache to store API responses")
    parser.add_argument("--config", "-c", type=str, default="default.conf", help="Configuration file for controlling parser")
    parser.add_argument("--logs", "-l", type=str, default=None, help="Optional output log file")
    parser.add_argument("--debug", action='store_true', default=False, help="Print debug logging")
    parser.add_argument("--notebook", action='store_true', default=False, help="Turn off logging to stdout for notebook use")
    parser.add_argument("--pages", type=str, default=None, help="Comma separated list of pages to process. Load all if left blank")
    return parser
