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
    if not config.has_section("meta"):
        config.add_section("meta")

    if args.cache:
        config.set("default", "cache", args.cache)

    if args.no_cache:
        config.set("default", "use_cache", "false")

    if args.flush_cache:
        config.set("default", "flush_cache", "true")
    
    if args.logs:
        config.set("default", "logdir", args.logs)

    config.set("default", "use_defaults", "true" if args.yes else 'false')

    if args.source:
        config.set("meta", "source", args.source)
    if args.authors:
        config.set("meta", "authors", ", ".join(args.authors))

    config.set("default", "debug", 'true' if args.debug else 'false')
    
    return config

def get_argparser() -> argparse.ArgumentParser:
    '''Creates command line argument parser to control the app'''

    parser = argparse.ArgumentParser(
        description="Extract 5e statblocks from images and PDFs"
    )
    parser.add_argument("target", type=str, nargs='+', help="Images or PDFs to search for monster statblocks")
    parser.add_argument("--source", "-s", type=str, help="Override source label for the statblocks processed")
    parser.add_argument("--authors", "-a", nargs='*', help="Override author label for the processed data")
    parser.add_argument("--overwrite", "-O", action='store_true', default=False, help="Overwrite existing file rather than appending")
    parser.add_argument("--url", "-u", type=str, help="Override URL label for processed data")
    parser.add_argument("--pages", type=str, default=None, help="Comma separated list of pages to process. Load all if left blank")

    parser.add_argument("--output", "-o", type=str, help="Output file containing statblocks", default=None)
    parser.add_argument("--format", '-f', type=str, help="Output format. Select 'none' to print statblocks to the terminal'", default='fvtt', choices=["none", "internal", 'text', 'fvtt'])
    
    parser.add_argument("--config", "-c", type=str, default="default.conf", help="Configuration file for controlling parser")
    parser.add_argument("--logs", "-l", type=str, default=None, help="Optional output log file")
    parser.add_argument("--debug", action='store_true', default=False, help="Print debug logging")
    
    parser.add_argument("--cache", "-C", type=str, default=".cache", help="Local cache directory to store API responses")
    parser.add_argument("--no-cache", "-N", action='store_true', help="Don't use a cache to save the result (useful when debugging the data loader")
    parser.add_argument("--flush-cache", "-F", action="store_true", help="Dont check the local cache but do save the result.")
    
    parser.add_argument("--yes", '-y', action='store_true', default=False, help="Auto accept defaults")
    parser.add_argument("--print", "-p", action='store_true', default=False, help='Print parsed statblocks to console')
    return parser
