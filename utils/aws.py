import boto3
import configparser
import logging
from typing import Dict
from utils.interacter import get_input

def setup_aws_config() -> Dict[str, str]:

        access_key = get_input("AWS ACCESS KEY", "Access key for an AWS role authorised to use Textract").strip()
        secret_key = get_input("AWS SECRET KEY", "Secret key for the authorised AWS role").strip()
        region = get_input("AWS REGION", "Default AWS Region").strip()

        config = {
            "access_key":access_key,
            "secret_key":secret_key,
            "region":region
        }

        return config

def get_authenticated_client(config: configparser.ConfigParser, logger: logging.Logger, service: str, **kwargs) -> boto3.client:

    if not config.has_section("aws"):
        logger.error("Cannot create {} client. No AWS credential present in config.".format(service))
        return None

    if not config.has_option("aws", "access_key"):
        logger.error("Cannot create {} client. aws.access_key required config.".format(service))
        return None

    if not config.has_option("aws", "secret_key"):
        logger.error("Cannot create {} client. aws.secret_key required config.".format(service))
        return None

    if not config.has_option("aws", "region"):
        logger.error("Cannot create {} client. aws.region required config.".format(service))
        return None

    boto3.setup_default_session(region_name=config.get("aws", "region"))

    return boto3.client(
        service,
        aws_access_key_id=config.get('aws', 'access_key'),
        aws_secret_access_key=config.get('aws', 'secret_key'),
    )